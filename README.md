IPR Prior-Art Checker 🛡️
A computational tool designed to detect prior-art and assess Intellectual Property Rights (IPR) risk at the pre-filing stage. This project utilizes Natural Language Processing (NLP) to compare candidate patent documents against a corpus of existing filings.

📌 Project Overview
In patent law, Novelty and Inventive Step are the primary hurdles for any inventor. This tool automates the initial search phase by:

Extracting raw text from patent PDFs.

Preprocessing data via tokenization, stop-word removal, and stemming.

Vectorizing text using TF-IDF (Term Frequency-Inverse Document Frequency).

Calculating similarity scores using Cosine Similarity against a dataset of 5,000+ patents.

🚀 Features
Real-time Similarity Engine: Powered by FastAPI and Scikit-learn.

BigQuery Integration: Fetches live patent data from Google’s Public Patent Dataset.

Tiered Risk Assessment: - 🟢 CLEAR: Low textual overlap (Original).

🟡 WARNING: Moderate overlap (Review claims).

🔴 CRITICAL: High overlap (Potential conflict).

Modern Dashboard: Clean UI with a dark/light mode toggle and average risk calculation.

🛠️ Tech Stack
Backend: Python (FastAPI, Uvicorn)

NLP Libraries: Scikit-learn, NLTK, PyMuPDF (fitz)

Frontend: HTML5, CSS3, Vanilla JavaScript

Database: Google Cloud BigQuery

📂 Project Structure
Plaintext
.
├── .venv/               # Virtual environment
├── credentials.json     # Google Cloud Service Account Key (Not in Repo)
├── index.html           # Frontend Dashboard
├── main.py              # FastAPI Similarity Engine
├── requirements.txt     # Python Dependencies
└── README.md            # Project Documentation
⚙️ Setup & Installation
1. Prerequisites
Python 3.10+

Google Cloud Platform (GCP) Account with BigQuery enabled.

2. Install Dependencies
Bash
# Create environment
python -m venv .venv
# Activate
.\\.venv\\Scripts\\activate 
# Install
pip install -r requirements.txt
3. Running the App
Ensure your credentials.json is in the root folder.

Start the backend:

Bash
uvicorn main:app --reload
Open index.html using the Go Live extension in VS Code.

⚖️ Legal Context
This tool situates itself within the Patents Act, 1970 (India) and TRIPS obligations. It serves as an accessible first-pass filter for inventors to identify potential conflicts before undergoing expensive legal examination.

Why this is a great EIPR Project:
Data Integrity: You aren't using a random CSV; you're using BigQuery, which shows cloud-native engineering.

Mathematical Basis: Using Cosine Similarity proves you understand the difference between "simple search" and "semantic similarity."

UX Design: The color-coded risk boxes show you've built this for a non-technical user (like a patent lawyer or an inventor).