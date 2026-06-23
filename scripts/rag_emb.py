import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


print("### RUNNING FULL-DATA EMBEDDING SCRIPT ###")


CHUNK_DIR = "../rag/chunks"
META_DIR = "../rag/metadata"
INDEX_PATH = "../rag/faiss.index"
EMB_PATH = "../rag/embeddings.npy"
EMBED_MODEL_NAME = os.getenv("RAG_EMBED_MODEL", "all-MiniLM-L6-v2")

CHUNK_DIR = "../rag/chunks"
print("CHUNK_DIR:", os.path.abspath(CHUNK_DIR))
print("FILES FOUND:", len(os.listdir(CHUNK_DIR)))


print("Embedding model:", EMBED_MODEL_NAME)
model = SentenceTransformer(EMBED_MODEL_NAME)

texts = []
ids = []

for fname in os.listdir(CHUNK_DIR):
    if not fname.endswith(".txt"):
        continue

    chunk_id = fname.replace(".txt", "")
    with open(os.path.join(CHUNK_DIR, fname), "r", encoding="utf-8") as f:
        text = f.read()

    texts.append(text)
    ids.append(chunk_id)

print(f"Embedding {len(texts)} chunks...")

embeddings = model.encode(
    texts,
    batch_size=16,
    show_progress_bar=True,
    convert_to_numpy=True
)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, INDEX_PATH)
np.save(EMB_PATH, embeddings)

with open(os.path.join(META_DIR, "chunk_ids.json"), "w") as f:
    json.dump(ids, f, indent=2)

print("FAISS index built and saved.")
