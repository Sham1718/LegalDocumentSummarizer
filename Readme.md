# Legal Document Summarizer (RAG-Based)

## Summary
An AI-powered Legal Document Summarizer that leverages Retrieval-Augmented Generation (RAG), semantic search, and NLP techniques to generate concise summaries and answer questions from complex legal documents.

---

# Overview

Legal Document Summarizer is an AI-driven application designed to simplify lengthy and complex legal documents by generating meaningful summaries and enabling semantic question-answering.

The project combines Natural Language Processing (NLP), semantic search, and Retrieval-Augmented Generation (RAG) to improve accessibility and understanding of legal judgments and documents.

The system processes legal documents through:
- Document chunking
- Sentence embeddings generation
- Vector similarity search using FAISS
- AI-based summarization
- Context-aware information retrieval

The project was developed to demonstrate the practical application of Generative AI and NLP techniques in the legal domain.

---

# Problem Statement

Legal documents are often:
- Extremely lengthy
- Difficult to understand for non-lawyers
- Time-consuming to analyze manually
- Challenging to search efficiently

This project solves these challenges by providing:
- Automatic legal document summarization
- Semantic search and retrieval
- AI-powered question answering
- Faster extraction of important information

through Retrieval-Augmented Generation and modern NLP techniques.

---

# Tools and Tech

## Backend & APIs
- Python
- FastAPI
- Uvicorn

## Machine Learning & NLP
- Transformers
- SentenceTransformers
- FAISS
- T5 Transformer Model
- TextRank Algorithm
- ROUGE Evaluation Metrics

## Data Processing
- NumPy
- Pandas
- JSON
- Pickle

## Development Tools
- Jupyter Notebook
- VS Code
- Git & GitHub

---

# Methods

## Document Processing Pipeline

### Document Chunking
Large legal documents are divided into smaller chunks for efficient processing and retrieval.

### Embedding Generation
Document chunks are converted into semantic vector embeddings using:

```text
all-MiniLM-L6-v2
```

### Vector Database
Embeddings are indexed using:

```text
FAISS
```

for efficient similarity search.

---

## Retrieval-Augmented Generation (RAG)

The RAG pipeline follows:

1. User submits a question
2. Query embedding is generated
3. Similar document chunks are retrieved from FAISS
4. Relevant context is passed to the summarization model
5. Context-aware responses are generated

---

## Summarization Techniques

### Abstractive Summarization
- T5 Transformer Model

### Extractive Summarization
- TextRank Algorithm

---

## Evaluation

Generated summaries are evaluated using:

- ROUGE-1
- ROUGE-2
- ROUGE-L

---

## API Services

- Document upload
- Semantic search
- Legal question answering
- Summary generation
- Context retrieval APIs

---

# Key Insights

- Learned Retrieval-Augmented Generation (RAG)
- Implemented semantic search using vector embeddings
- Worked with FAISS vector databases
- Improved understanding of NLP pipelines
- Practiced transformer-based summarization
- Learned evaluation using ROUGE metrics
- Built AI-powered question-answering workflows
- Applied Generative AI techniques to legal documents

---

# How to Run Project

## Clone Repository

```bash
git clone https://github.com/Sham1718/LegalDocumentSummarizer.git
```

---

## Navigate to Project

```bash
cd LegalDocumentSummarizer
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run FastAPI Server

```bash
uvicorn app:app --reload
```

---

## Default Server

```text
http://127.0.0.1:8000
```

---

# Result

Successfully developed an AI-powered Legal Document Summarizer capable of:

- Processing lengthy legal documents
- Generating concise summaries
- Performing semantic document retrieval
- Answering context-aware legal queries
- Using Retrieval-Augmented Generation (RAG)
- Implementing vector similarity search with FAISS
- Applying transformer-based NLP models

The project demonstrates strong understanding of NLP, Generative AI, vector databases, and modern AI application development.

---

# Author and Contact

## Author
Shyam

Computer Engineering Student

## Contact
- GitHub: https://github.com/Sham1718
- Portfolio: https://shyam-neon.vercel.app/