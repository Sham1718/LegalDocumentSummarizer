import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNK_DIR = "../rag/chunks"
META_DIR = "../rag/metadata"
INDEX_PATH = "../rag/faiss.index"

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load chunk IDs
with open(os.path.join(META_DIR, "chunk_ids.json"), "r") as f:
    chunk_ids = json.load(f)

# ---- CONFIG ----
TOP_K = 3
DISTANCE_THRESHOLD = 1.2

def search(query):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, TOP_K)

    results = []
    valid = False

    for dist, idx in zip(distances[0], indices[0]):
        if dist < DISTANCE_THRESHOLD:
            valid = True
            chunk_id = chunk_ids[idx]
            chunk_path = os.path.join(CHUNK_DIR, f"{chunk_id}.txt")
            with open(chunk_path, "r", encoding="utf-8") as f:
                text = f.read()
            results.append((chunk_id, text, dist))

    return valid, results


if __name__ == "__main__":
    query = "What were the main facts of the case?"
    valid, results = search(query)

    print("\n==============================")
    print("LEGAL QUESTION")
    print("==============================")
    print(query)

    print("\nANSWER")
    if not valid:
        print("The answer is not available in the provided document.")
    else:
        print("Relevant context found in the following document segments:")

        print("\nSOURCES")
        for i, (cid, text, dist) in enumerate(results, 1):
            print(f"[{i}] {cid} (distance={round(dist,3)}) {text[:800]}")

    print("==============================\n")
