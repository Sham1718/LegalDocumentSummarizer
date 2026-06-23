import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

CHUNK_DIR = "../rag/chunks"
META_DIR = "../rag/metadata"
INDEX_PATH = "../rag/faiss.index"

# Models
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
tokenizer = T5Tokenizer.from_pretrained("t5-small")
gen_model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Load FAISS + IDs
index = faiss.read_index(INDEX_PATH)
with open(os.path.join(META_DIR, "chunk_ids.json"), "r") as f:
    chunk_ids = json.load(f)

def retrieve(query, top_k=3):
    q_emb = embed_model.encode([query], convert_to_numpy=True)
    _, idxs = index.search(q_emb, top_k)
    chunks = []
    for i in idxs[0]:
        cid = chunk_ids[i]
        with open(os.path.join(CHUNK_DIR, f"{cid}.txt"), "r", encoding="utf-8") as f:
            chunks.append((cid, f.read()))
    return chunks

def generate_answer(query, chunks):
    context = "\n\n".join([c[1][:1200] for c in chunks])  # cap context
    prompt = f"question: {query}\ncontext: {context}"
    input_ids = tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=512)

    out_ids = gen_model.generate(
        input_ids,
        max_length=150,
        min_length=60,
        num_beams=4,
        length_penalty=1.5,
        early_stopping=True
    )
    return tokenizer.decode(out_ids[0], skip_special_tokens=True)

if __name__ == "__main__":
    query = "What did the court say about breach of contract damages?"
    chunks = retrieve(query, top_k=3)
    answer = generate_answer(query, chunks)

    print("QUESTION:")
    print(query)
    print("\nANSWER:")
    print(answer)
    print("\nCITATIONS:")
    for i, (cid, _) in enumerate(chunks, 1):
        print(f"[{i}] {cid}")
