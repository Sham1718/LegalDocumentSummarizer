import json
import os
import re
from typing import Dict, List, Optional, Tuple, Union

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(__file__)
CHUNK_DIR = os.path.join(BASE_DIR, "../rag/chunks")
META_DIR = os.path.join(BASE_DIR, "../rag/metadata")
INDEX_PATH = os.path.join(BASE_DIR, "../rag/faiss.index")
CHUNK_IDS_PATH = os.path.join(META_DIR, "chunk_ids.json")

# ===============================
# CONFIG
# ===============================
TOP_K = int(os.getenv("RAG_TOP_K", "4"))
DISTANCE_THRESHOLD = 1.2
DISTANCE_MARGIN = 2.5
MIN_VALID_CHUNKS = 1
MAX_CONTEXT_CHARS = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "1800"))

EMBED_MODEL_NAME = os.getenv(
    "RAG_EMBED_MODEL",
    "paraphrase-multilingual-MiniLM-L12-v2",
)
GEN_MODEL_NAME = os.getenv("RAG_GEN_MODEL", "google/flan-t5-small")
GEN_MAX_INPUT_TOKENS = int(os.getenv("RAG_GEN_MAX_INPUT_TOKENS", "512"))
GEN_MAX_NEW_TOKENS = int(os.getenv("RAG_GEN_MAX_NEW_TOKENS", "160"))
GEN_NUM_BEAMS = int(os.getenv("RAG_GEN_NUM_BEAMS", "2"))
TRANSLATE_MODEL_NAME = os.getenv("RAG_TRANSLATE_MODEL", "google/mt5-small")
HI_TRANSLATE_MODEL_NAME = os.getenv("RAG_HI_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-hi")
TRANSLATE_MAX_NEW_TOKENS = int(os.getenv("RAG_TRANSLATE_MAX_NEW_TOKENS", "140"))
TRANSLATE_NUM_BEAMS = int(os.getenv("RAG_TRANSLATE_NUM_BEAMS", "2"))

NON_LEGAL_KEYWORDS = [
    "modi",
    "rahul gandhi",
    "actor",
    "movie",
    "cricket",
    "politics",
    "biography",
    "who is",
    "what is your name",
]

LANG_LABELS = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
}

LANG_ALIASES = {
    "english": "en",
    "hindi": "hi",
    "tamil": "ta",
    "tam": "ta",
    "telugu": "te",
    "telegu": "te",
    "tel": "te",
    "bengali": "bn",
    "bangla": "bn",
    "marathi": "mr",
    "mar": "mr",
    "gujarati": "gu",
    "guj": "gu",
}

_embedder: Optional[SentenceTransformer] = None
_tokenizer: Optional[AutoTokenizer] = None
_generator: Optional[AutoModelForSeq2SeqLM] = None
_translator_tokenizer: Optional[AutoTokenizer] = None
_translator_model: Optional[AutoModelForSeq2SeqLM] = None
_hi_translator_tokenizer: Optional[AutoTokenizer] = None
_hi_translator_model: Optional[AutoModelForSeq2SeqLM] = None
_marian_tokenizers: Dict[str, AutoTokenizer] = {}
_marian_models: Dict[str, AutoModelForSeq2SeqLM] = {}
_nllb_tokenizer: Optional[AutoTokenizer] = None
_nllb_model: Optional[AutoModelForSeq2SeqLM] = None
_index: Optional[faiss.Index] = None
_chunk_ids: Optional[List[str]] = None

MARIAN_MODEL_NAMES = {
    "hi": os.getenv("RAG_HI_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-hi"),
    "ta": os.getenv("RAG_TA_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-ta"),
    "te": os.getenv("RAG_TE_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-te"),
    "bn": os.getenv("RAG_BN_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-bn"),
    "mr": os.getenv("RAG_MR_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-mr"),
    "gu": os.getenv("RAG_GU_TRANSLATE_MODEL", "Helsinki-NLP/opus-mt-en-gu"),
}
NLLB_MODEL_NAME = os.getenv("RAG_NLLB_TRANSLATE_MODEL", "")
NLLB_LANG_CODES = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "bn": "ben_Beng",
    "mr": "mar_Deva",
    "gu": "guj_Gujr",
}


def _detect_language(text: str) -> str:
    for ch in text:
        code = ord(ch)
        if 0x0900 <= code <= 0x097F:
            return "hi"
        if 0x0980 <= code <= 0x09FF:
            return "bn"
        if 0x0A80 <= code <= 0x0AFF:
            return "gu"
        if 0x0B80 <= code <= 0x0BFF:
            return "ta"
        if 0x0C00 <= code <= 0x0C7F:
            return "te"
    return "en"


def _normalize_language(question: str, language: str) -> str:
    if not language or language.lower() == "auto":
        return _detect_language(question)
    raw = language.lower()
    if "-" in raw:
        raw = raw.split("-", 1)[0]
    if "_" in raw:
        raw = raw.split("_", 1)[0]
    return LANG_ALIASES.get(raw, raw)


def _is_multilingual_embedder() -> bool:
    name = EMBED_MODEL_NAME.lower()
    return "multilingual" in name or "muse" in name or "distiluse" in name


def _ensure_loaded() -> None:
    global _embedder, _tokenizer, _generator, _index, _chunk_ids

    if _index is None:
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")
        _index = faiss.read_index(INDEX_PATH)

    if _chunk_ids is None:
        if not os.path.exists(CHUNK_IDS_PATH):
            raise FileNotFoundError(f"Chunk metadata not found: {CHUNK_IDS_PATH}")
        with open(CHUNK_IDS_PATH, "r", encoding="utf-8") as f:
            _chunk_ids = json.load(f)

    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)

    if _tokenizer is None or _generator is None:
        _tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL_NAME, use_fast=False, legacy=True)
        _generator = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL_NAME)
        _generator.eval()


def _ensure_translator_loaded() -> None:
    global _translator_tokenizer, _translator_model
    if _translator_tokenizer is None or _translator_model is None:
        _translator_tokenizer = AutoTokenizer.from_pretrained(
            TRANSLATE_MODEL_NAME,
            use_fast=False,
            legacy=True,
        )
        _translator_model = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATE_MODEL_NAME)
        _translator_model.eval()


def _ensure_hi_translator_loaded() -> None:
    global _hi_translator_tokenizer, _hi_translator_model
    if _hi_translator_tokenizer is None or _hi_translator_model is None:
        _hi_translator_tokenizer = AutoTokenizer.from_pretrained(
            HI_TRANSLATE_MODEL_NAME,
            use_fast=False,
            legacy=True,
        )
        _hi_translator_model = AutoModelForSeq2SeqLM.from_pretrained(HI_TRANSLATE_MODEL_NAME)
        _hi_translator_model.eval()


def _ensure_marian_loaded(target_lang: str) -> bool:
    model_name = MARIAN_MODEL_NAMES.get(target_lang)
    if not model_name:
        return False
    if target_lang not in _marian_tokenizers or target_lang not in _marian_models:
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False, legacy=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.eval()
        _marian_tokenizers[target_lang] = tokenizer
        _marian_models[target_lang] = model
    return True


def _ensure_nllb_loaded() -> None:
    global _nllb_tokenizer, _nllb_model
    if not NLLB_MODEL_NAME:
        raise RuntimeError("NLLB model is disabled")
    if _nllb_tokenizer is None or _nllb_model is None:
        _nllb_tokenizer = AutoTokenizer.from_pretrained(NLLB_MODEL_NAME, use_fast=False, legacy=True)
        _nllb_model = AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL_NAME)
        _nllb_model.eval()


def _build_prompt(question: str, context: str, language: str) -> str:
    _ = LANG_LABELS.get(language, language or "English")
    return (
        "You are a legal assistant.\n"
        "Answer strictly from the given legal context.\n"
        "If context is insufficient, say that clearly.\n"
        "Respond in English.\n\n"
        f"Question: {question}\n"
        f"Legal Context:\n{context}\n\n"
        "Answer:"
    )


def _is_usable_translation(source: str, candidate: str) -> bool:
    if not candidate or "<extra_id_" in candidate:
        return False
    if candidate.lower() == source.lower():
        return False
    if len(candidate) < max(12, int(len(source) * 0.35)):
        return False
    return True


def _translate_query_to_english(question: str) -> str:
    assert _tokenizer is not None
    assert _generator is not None
    prompt = f"Translate this legal question to English:\n{question}\nEnglish:"
    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
    outputs = _generator.generate(
        inputs["input_ids"],
        attention_mask=inputs.get("attention_mask"),
        max_new_tokens=64,
        do_sample=False,
        num_beams=4,
    )
    translated = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return translated or question


def _translate_answer(answer: str, target_lang: str) -> str:
    if target_lang == "en":
        return answer
    if target_lang in MARIAN_MODEL_NAMES:
        try:
            if target_lang == "hi":
                _ensure_hi_translator_loaded()
                tokenizer = _hi_translator_tokenizer
                model = _hi_translator_model
            else:
                _ensure_marian_loaded(target_lang)
                tokenizer = _marian_tokenizers.get(target_lang)
                model = _marian_models.get(target_lang)

            if tokenizer is None or model is None:
                return answer

            inputs = tokenizer(answer, return_tensors="pt", truncation=True, max_length=384)
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_new_tokens=TRANSLATE_MAX_NEW_TOKENS,
                num_beams=TRANSLATE_NUM_BEAMS,
            )
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            if _is_usable_translation(answer, translated):
                return translated
        except Exception:
            pass
    if target_lang in NLLB_LANG_CODES:
        try:
            _ensure_nllb_loaded()
            assert _nllb_tokenizer is not None
            assert _nllb_model is not None
            _nllb_tokenizer.src_lang = NLLB_LANG_CODES["en"]
            inputs = _nllb_tokenizer(answer, return_tensors="pt", truncation=True, max_length=384)
            forced_bos_id = _nllb_tokenizer.convert_tokens_to_ids(NLLB_LANG_CODES[target_lang])
            outputs = _nllb_model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                forced_bos_token_id=forced_bos_id,
                max_new_tokens=TRANSLATE_MAX_NEW_TOKENS,
                num_beams=TRANSLATE_NUM_BEAMS,
            )
            translated = _nllb_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            if _is_usable_translation(answer, translated):
                return translated
        except Exception:
            pass
    try:
        _ensure_translator_loaded()
    except Exception:
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source="en", target=target_lang).translate(answer)
            return translated or answer
        except Exception:
            return answer
    assert _translator_tokenizer is not None
    assert _translator_model is not None
    lang_label = LANG_LABELS.get(target_lang, target_lang)
    prompt = f"Translate this legal answer to {lang_label}:\n{answer}\nTranslated:"
    inputs = _translator_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384)
    outputs = _translator_model.generate(
        inputs["input_ids"],
        attention_mask=inputs.get("attention_mask"),
        max_new_tokens=TRANSLATE_MAX_NEW_TOKENS,
        do_sample=False,
        num_beams=TRANSLATE_NUM_BEAMS,
    )
    translated = _translator_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    if not _is_usable_translation(answer, translated):
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source="en", target=target_lang).translate(answer)
            if _is_usable_translation(answer, translated):
                return translated
            return answer
        except Exception:
            return answer
    return translated or answer


def _build_answer_explanation(question: str, answer: str, retrieved: List[Dict]) -> str:
    if not retrieved:
        return "No relevant legal chunks were retrieved, so explanation is unavailable."

    top_chunks = retrieved[:2]
    evidence_lines: List[str] = []
    for item in top_chunks:
        first_sentence = re.split(r"(?<=[.!?])\s+", item["text"])[0].strip()
        if not first_sentence:
            first_sentence = item["text"][:180].strip()
        evidence_lines.append(f"[{item['chunk_id']}] {first_sentence[:220]}")

    return (
        f"Question: {question}\n"
        f"Answer summary: {answer}\n"
        f"Reasoning: The answer is based on {len(retrieved)} retrieved legal chunks "
        f"ranked by semantic similarity. Key evidence: {' | '.join(evidence_lines)}"
    )[:1400]


def _extractive_fallback(question: str, retrieved: List[Dict]) -> str:
    if not retrieved:
        return "The answer could not be clearly determined from the document."
    stop_words = {
        "what", "which", "where", "when", "about", "court", "does", "did",
        "have", "has", "had", "were", "was", "with", "from", "this", "that",
        "under", "into", "your", "there", "their"
    }
    keywords = [
        w for w in re.findall(r"[a-zA-Z]{3,}", question.lower())
        if w not in stop_words
    ]
    candidates = []
    for item in retrieved:
        for sent in re.split(r"(?<=[.!?])\s+", item["text"]):
            sent = sent.strip()
            if len(sent) < 30:
                continue
            s_low = sent.lower()
            score = sum(1 for k in keywords if k in s_low)
            if score > 0:
                candidates.append((score, item["distance"], sent))

    if candidates:
        # Prefer high keyword overlap and closer chunks.
        candidates.sort(key=lambda x: (-x[0], x[1]))
        top = [c[2] for c in candidates[:2]]
        return " ".join(top)[:520]

    # Last resort if no keyword match in any sentence.
    first_chunk_sents = re.split(r"(?<=[.!?])\s+", retrieved[0]["text"])
    return " ".join(first_chunk_sents[:2]).strip()[:420] or "The answer could not be clearly determined from the document."


def ask_rag(
    question: str,
    language: str = "auto",
    top_k: int = TOP_K,
    return_chunks: bool = False,
    return_explanation: bool = False,
    gen_max_new_tokens: Optional[int] = None,
) -> Union[
    Tuple[str, List[str]],
    Tuple[str, List[str], List[Dict], str],
    Tuple[str, List[str], List[Dict], str, str],
]:
    try:
        _ensure_loaded()
    except Exception as exc:
        message = f"RAG resources are not ready: {exc}"
        return (message, [], [], "en") if return_chunks else (message, [])
    assert _embedder is not None
    assert _tokenizer is not None
    assert _generator is not None
    assert _index is not None
    assert _chunk_ids is not None

    question = (question or "").strip()
    target_lang = _normalize_language(question, language)

    if not question:
        message = "Please provide a non-empty legal question."
        localized = _translate_answer(message, target_lang)
        if return_chunks and return_explanation:
            return (localized, [], [], target_lang, localized)
        if return_chunks:
            return (localized, [], [], target_lang)
        return (localized, [])

    q_lower = question.lower()
    if any(word in q_lower for word in NON_LEGAL_KEYWORDS):
        message = "This system answers only questions related to legal documents."
        localized = _translate_answer(message, target_lang)
        if return_chunks and return_explanation:
            return (localized, [], [], target_lang, localized)
        if return_chunks:
            return (localized, [], [], target_lang)
        return (localized, [])

    if target_lang == "en" or _is_multilingual_embedder():
        retrieval_query = question
    else:
        retrieval_query = _translate_query_to_english(question)
    q_emb = _embedder.encode([retrieval_query], convert_to_numpy=True).astype(np.float32)
    distances, indices = _index.search(q_emb, top_k)

    retrieved: List[Dict] = []
    seen_ids = set()

    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(_chunk_ids):
            continue

        cid = _chunk_ids[idx]
        if cid in seen_ids:
            continue

        chunk_path = os.path.join(CHUNK_DIR, f"{cid}.txt")
        if not os.path.exists(chunk_path):
            continue

        with open(chunk_path, "r", encoding="utf-8") as f:
            chunk_text = f.read().strip()

        if not chunk_text:
            continue

        seen_ids.add(cid)
        retrieved.append(
            {
                "chunk_id": cid,
                "distance": float(dist),
                "text": chunk_text,
            }
        )

    retrieved.sort(key=lambda x: x["distance"])
    if retrieved:
        best_distance = retrieved[0]["distance"]
        dynamic_threshold = max(DISTANCE_THRESHOLD, best_distance + DISTANCE_MARGIN)
        retrieved = [item for item in retrieved if item["distance"] <= dynamic_threshold]

    if len(retrieved) < MIN_VALID_CHUNKS:
        message = "The question cannot be answered using the provided legal documents."
        localized = _translate_answer(message, target_lang)
        if return_chunks and return_explanation:
            return (localized, [], retrieved, target_lang, localized)
        if return_chunks:
            return (localized, [], retrieved, target_lang)
        return (localized, [])

    context_parts: List[str] = []
    context_len = 0
    for item in retrieved:
        text = item["text"]
        if context_len + len(text) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - context_len
            if remaining > 80:
                context_parts.append(text[:remaining])
            break
        context_parts.append(text)
        context_len += len(text)

    context = "\n\n".join(context_parts)
    prompt = _build_prompt(question, context, target_lang)

    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=GEN_MAX_INPUT_TOKENS,
    )
    max_new_tokens = gen_max_new_tokens or GEN_MAX_NEW_TOKENS
    outputs = _generator.generate(
        inputs["input_ids"],
        attention_mask=inputs.get("attention_mask"),
        max_new_tokens=max_new_tokens,
        do_sample=False,
        num_beams=GEN_NUM_BEAMS,
    )

    answer = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    if not answer or answer.lower().startswith(("question", "legal context", "answer")) or "<extra_id_" in answer:
        answer = _extractive_fallback(question, retrieved)
    explanation = _build_answer_explanation(question, answer, retrieved)
    answer = _translate_answer(answer, target_lang)
    explanation = _translate_answer(explanation, target_lang)

    sources = [item["chunk_id"] for item in retrieved]
    if return_chunks and return_explanation:
        return (answer, sources, retrieved, target_lang, explanation)
    if return_chunks:
        return (answer, sources, retrieved, target_lang)
    return (answer, sources)
