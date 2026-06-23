import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Paths
BASE_DIR = os.path.dirname(__file__)
CHUNK_DIR = os.path.join(BASE_DIR, "../rag/chunks")
META_DIR = os.path.join(BASE_DIR, "../rag/metadata")
INDEX_PATH = os.path.join(BASE_DIR, "../rag/faiss.index")

# Models
embedder = SentenceTransformer("all-MiniLM-L6-v2")
tokenizer = T5Tokenizer.from_pretrained("t5-small")
generator = T5ForConditionalGeneration.from_pretrained("t5-small")

# Load FAISS
index = faiss.read_index(INDEX_PATH)
with open(os.path.join(META_DIR, "chunk_ids.json"), "r") as f:
    chunk_ids = json.load(f)

DISTANCE_THRESHOLD = 1.2
TOP_K = 3


def ask_rag(question: str):
    q_emb = embedder.encode([question], convert_to_numpy=True)
    distances, indices = index.search(q_emb, TOP_K)

    context_chunks = []
    sources = []

    for dist, idx in zip(distances[0], indices[0]):
        if dist < DISTANCE_THRESHOLD:
            cid = chunk_ids[idx]
            with open(os.path.join(CHUNK_DIR, cid + ".txt"), "r", encoding="utf-8") as f:
                context_chunks.append(f.read())
            sources.append(cid)

    if not context_chunks:
        return "The answer is not available in the provided document.", []

    context = " ".join(context_chunks)[:2000]

    prompt = (
        "Answer the question strictly using the legal context below. "
        "Rewrite the answer in simple, plain English so a non-legal user can understand it.\n\n"
        f"Context:\n{context}\n\nQuestion:\n{question}"
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = generator.generate(**inputs, max_length=200)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer, sources
