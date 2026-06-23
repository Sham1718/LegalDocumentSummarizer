import os
import re
import json

INPUT_DIR = "../in_abs/train-data/train-data/judgement"
OUTPUT_DIR = "../rag/chunks"
META_DIR = "../rag/metadata"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

CHUNK_WORDS = 500
OVERLAP_WORDS = 50

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_words(words, size, overlap):
    chunks = []
    start = 0
    n = len(words)
    while start < n:
        end = min(start + size, n)
        chunks.append(words[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks

def main():
    metadata = []

    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".txt"):
            continue

        case_id = fname.replace(".txt", "")
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            text = clean_text(f.read())

        words = text.split()
        chunks = chunk_words(words, CHUNK_WORDS, OVERLAP_WORDS)

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{case_id}_chunk_{idx}"
            chunk_text = " ".join(chunk)

            out_path = os.path.join(OUTPUT_DIR, f"{chunk_id}.txt")
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(chunk_text)

            metadata.append({
                "chunk_id": chunk_id,
                "case_id": case_id,
                "chunk_index": idx,
                "word_count": len(chunk)
            })

        print(f"Chunked {case_id}: {len(chunks)} chunks")

    with open(os.path.join(META_DIR, "chunks_meta.json"), "w", encoding="utf-8") as m:
        json.dump(metadata, m, indent=2)

    print("RAG chunking completed.")

if __name__ == "__main__":
    main()
