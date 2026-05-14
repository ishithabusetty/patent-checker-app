import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials.json"

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz
import pandas as pd
from google.cloud import bigquery
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# 1. Initialize FastAPI and Allow Local Connections (CORS)
app = FastAPI(title="Patent Similarity Checker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Download NLTK data (runs once)
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

# 3. Text Processing Utilities
def preprocess_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    processed_tokens = [stemmer.stem(word) for word in text.split() if word not in stop_words]
    return ' '.join(processed_tokens)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc: text += page.get_text("text") + " "
        doc.close()
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")
    return text.strip()

# 4. Load BigQuery Data & Fit Model at Startup
print("Initializing Backend: Fetching BigQuery data and building TF-IDF matrix...")
project_id = 'patent-checker-app' # MAKE SURE THIS IS YOUR ACTUAL PROJECT ID
# This explicitly tells the client to look at your JSON file
client = bigquery.Client.from_service_account_json("./credentials.json")
query = """
    SELECT publication_number, ANY_VALUE(abstract.text) AS abstract_text
    FROM `patents-public-data.patents.publications`, UNNEST(abstract_localized) AS abstract
    WHERE country_code = 'US' AND abstract.language = 'en'
    GROUP BY publication_number LIMIT 5000
"""
corpus_df = client.query(query).to_dataframe().dropna(subset=['abstract_text'])
corpus_df['processed_abstract'] = corpus_df['abstract_text'].apply(preprocess_text)

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus_df['processed_abstract'])
print("Backend Ready.")

# 5. Core API Endpoint
@app.post("/check-prior-art")
async def check_prior_art(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")
    
    try:
        file_bytes = await file.read()
        candidate_text = extract_text_from_pdf(file_bytes)
        
        cleaned_candidate = preprocess_text(candidate_text)
        candidate_vector = vectorizer.transform([cleaned_candidate])
        similarity_scores = cosine_similarity(candidate_vector, tfidf_matrix).flatten()
        top_indices = similarity_scores.argsort()[-5:][::-1]
        
        results = []
        for idx in top_indices:
            score = float(similarity_scores[idx]) * 100
            risk = "High" if score > 75 else "Moderate" if score > 40 else "Low"
            results.append({
                "publication_number": corpus_df.iloc[idx]['publication_number'],
                "similarity_score": round(score, 2),
                "risk_level": risk,
                "abstract_snippet": corpus_df.iloc[idx]['abstract_text'][:200] + "..."
            })
            
        cumulative_score = round(sum(m['similarity_score'] for m in results), 2)
        highest_score = results[0]['similarity_score'] if results else 0
        
        if highest_score > 75:
            overall_risk = "CRITICAL: High probability of prior-art conflict."
            final_verdict = "Review your paper immediately! It is highly similar to existing patents. Needs major improvements."
        elif highest_score > 40:
            overall_risk = "WARNING: Moderate overlap detected. Review claims carefully."
            final_verdict = "Not that similar, which is good, but review the moderately similar patents to be safe. Can be improved."
        else:
            overall_risk = "CLEAR: Low textual overlap with existing corpus."
            final_verdict = "No significant similarity found! Considered original."
 
        return JSONResponse(content={
            "status": "success",
            "message": "Prior-art analysis complete.",
            "overall_risk_assessment": overall_risk,
            "max_similarity_found": highest_score,
            "cumulative_similarity_score": cumulative_score,
            "final_verdict": final_verdict,
            "extracted_text_length": len(candidate_text),
            "top_matches": results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))