import os
import re
import fitz
import nltk
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# 1. AUTHENTICATION
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials.json"

app = FastAPI()

# AGGRESSIVE CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

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

print("Initializing Backend: Fetching BigQuery data...")
project_id = 'patent-checker-app' 
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

@app.post("/check-prior-art")
async def check_prior_art(file: UploadFile = File(...)):
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
            results.append({
                "publication_number": corpus_df.iloc[idx]['publication_number'],
                "similarity_score": round(score, 2),
                "abstract_snippet": corpus_df.iloc[idx]['abstract_text'][:250] + "..."
            })
            
        highest_score = results[0]['similarity_score'] if results else 0
        avg_score = round(sum(m['similarity_score'] for m in results) / len(results), 2) if results else 0
        
        if highest_score > 75:
            risk_title = "CRITICAL: High probability of prior-art conflict."
            verdict = "Review your paper immediately! Highly similar to existing patents."
        elif highest_score > 40:
            risk_title = "WARNING: Moderate overlap detected. Review claims carefully."
            verdict = "Not that similar, but review moderately similar patents. Can be improved."
        else:
            risk_title = "CLEAR: Low textual overlap with existing corpus."
            verdict = "No significant similarity found! Considered original."

        return {
            "status": "success",
            "overall_risk_assessment": risk_title,
            "max_similarity_found": highest_score,
            "average_similarity_score": avg_score,
            "final_verdict": verdict,
            "top_matches": results
        }
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})