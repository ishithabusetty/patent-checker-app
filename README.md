# IPR Prior-Art Checker 🛡️

A high-fidelity computational tool designed to detect prior-art and assess Intellectual Property Rights (IPR) risk at the pre-filing stage. This project leverages Natural Language Processing (NLP) to compare candidate patent documents against a corpus of existing global filings.

## 📌 Project Overview

In patent law, **Novelty** and **Inventive Step** are the primary hurdles for any inventor. This tool automates the initial search phase by:

- **PDF Text Extraction:** Utilizing `PyMuPDF` for high-accuracy text recovery from patent documents.
- **NLP Preprocessing:** Implementing tokenization, stop-word removal, and Porter Stemming to normalize legal text.
- **Vectorization:** Transforming text into numerical features using **TF-IDF** (Term Frequency-Inverse Document Frequency).
- **Similarity Engine:** Calculating semantic proximity using **Cosine Similarity** against a dataset of 5,000+ patents fetched via Google BigQuery.

## 🚀 Key Features

- **Real-time Similarity Engine:** High-performance backend powered by **FastAPI** and **Scikit-learn**.
- **BigQuery Integration:** Live data pipeline fetching patent abstracts from the `patents-public-data` corpus.
- **Dynamic Risk Dashboard:**
    - 🟢 **CLEAR:** Low textual overlap (Highly original).
    - 🟡 **WARNING:** Moderate overlap (Review claims carefully).
    - 🔴 **CRITICAL:** High overlap (Probability of prior-art conflict).
- **Statistical Assessment:** Provides both **Maximum Similarity** (peak risk) and **Average Similarity** (contextual risk).

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **NLP & ML:** Scikit-learn, NLTK, PyMuPDF (fitz)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Cloud Infrastructure:** Google Cloud Platform (BigQuery API)

## 📂 Project Structure

```text
.
├── .venv/               # Isolated virtual environment
├── credentials.json     # Google Cloud Service Account Key (Restricted)
├── index.html           # High-contrast Risk Dashboard
├── main.py              # FastAPI Similarity Engine & BigQuery Pipeline
├── requirements.txt     # Python Library Manifest
└── README.md            # Project Documentation
```

## ⚙️ Setup & Installation

### 1. Prerequisites

- **Python 3.10+** installed on your local machine.
- A valid **Google Cloud Service Account key** (`credentials.json`) with **BigQuery Viewer** permissions.

### 2. Environment Setup

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment (Windows)
.\\.venv\\Scripts\\activate

# Activate the environment (Mac/Linux)
# source .venv/bin/activate

# Install required Python libraries
pip install -r requirements.txt
```

### 3. Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Once the terminal displays Backend Ready, open index.html using the Go Live extension in VS Code.

## ⚖️ Legal & EIPR Context

This tool situates itself within the framework of the Patents Act, 1970 (India) and international TRIPS obligations. By providing a reproducible, mathematical basis for novelty detection, it serves as an essential first-pass filter for inventors to identify potential conflicts before undergoing expensive formal examination.

## Why this is a great EIPR Project:

Data Integrity: You aren't using a random CSV; you're using BigQuery, which shows cloud-native engineering.

Mathematical Basis: Using Cosine Similarity proves you understand the difference between "simple search" and "semantic similarity."

UX Design: The color-coded risk boxes show you've built this for a non-technical user (like a patent lawyer or an inventor).