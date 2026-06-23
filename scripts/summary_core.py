from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer
import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, T5ForConditionalGeneration, T5Tokenizer

_textrank = TextRankSummarizer()
_t5_tok = None
_t5 = None

_mt5_tok = None
_mt5 = None
_marian_tokenizers = {}
_marian_models = {}
_nllb_tok = None
_nllb = None

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


def _normalize_language(text: str, language: str) -> str:
    if not language or language.lower() == "auto":
        return _detect_language(text)
    raw = language.lower()
    if "-" in raw:
        raw = raw.split("-", 1)[0]
    if "_" in raw:
        raw = raw.split("_", 1)[0]
    return LANG_ALIASES.get(raw, raw)


def _ensure_t5_loaded():
    global _t5_tok, _t5
    if _t5_tok is None or _t5 is None:
        _t5_tok = T5Tokenizer.from_pretrained("t5-small", use_fast=False, legacy=True)
        _t5 = T5ForConditionalGeneration.from_pretrained("t5-small")


def _ensure_mt5_loaded():
    global _mt5_tok, _mt5
    if _mt5_tok is None or _mt5 is None:
        _mt5_tok = AutoTokenizer.from_pretrained("google/mt5-small", use_fast=False)
        _mt5 = AutoModelForSeq2SeqLM.from_pretrained("google/mt5-small")


def _ensure_marian_loaded(target_lang: str):
    model_name = MARIAN_MODEL_NAMES.get(target_lang)
    if not model_name:
        return None, None
    if target_lang not in _marian_tokenizers or target_lang not in _marian_models:
        _marian_tokenizers[target_lang] = AutoTokenizer.from_pretrained(
            model_name,
            use_fast=False,
            legacy=True,
        )
        _marian_models[target_lang] = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return _marian_tokenizers[target_lang], _marian_models[target_lang]


def _ensure_nllb_loaded():
    global _nllb_tok, _nllb
    if not NLLB_MODEL_NAME:
        raise RuntimeError("NLLB model is disabled")
    if _nllb_tok is None or _nllb is None:
        _nllb_tok = AutoTokenizer.from_pretrained(NLLB_MODEL_NAME, use_fast=False, legacy=True)
        _nllb = AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL_NAME)


def _is_usable_translation(source: str, candidate: str) -> bool:
    if not candidate or "<extra_id_" in candidate:
        return False
    if candidate.lower() == source.lower():
        return False
    if len(candidate) < max(12, int(len(source) * 0.35)):
        return False
    return True


def _translate_text(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text

    try:
        tokenizer, model = _ensure_marian_loaded(target_lang)
        if tokenizer is not None and model is not None:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=384)
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_new_tokens=240,
                num_beams=4,
            )
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            if _is_usable_translation(text, translated):
                return translated
    except Exception:
        pass

    try:
        if target_lang in NLLB_LANG_CODES:
            _ensure_nllb_loaded()
            _nllb_tok.src_lang = NLLB_LANG_CODES["en"]
            inputs = _nllb_tok(text, return_tensors="pt", truncation=True, max_length=512)
            forced_bos_id = _nllb_tok.convert_tokens_to_ids(NLLB_LANG_CODES[target_lang])
            outputs = _nllb.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                forced_bos_token_id=forced_bos_id,
                max_new_tokens=240,
                num_beams=4,
            )
            translated = _nllb_tok.decode(outputs[0], skip_special_tokens=True).strip()
            if _is_usable_translation(text, translated):
                return translated
    except Exception:
        pass

    try:
        _ensure_mt5_loaded()
        lang_label = LANG_LABELS.get(target_lang, target_lang)
        prompt = f"Translate this legal summary to {lang_label}:\n{text}\nTranslated:"
        inputs = _mt5_tok(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = _mt5.generate(
            **inputs,
            max_new_tokens=240,
            num_beams=4,
            early_stopping=True,
        )
        translated = _mt5_tok.decode(outputs[0], skip_special_tokens=True)
        if _is_usable_translation(text, translated):
            return translated
    except Exception:
        pass
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="en", target=target_lang).translate(text)
        if _is_usable_translation(text, translated):
            return translated
        return text
    except Exception:
        pass
    return text


def summarize_textrank(text: str, sentence_count: int = 10, language: str = "en") -> str:
    target_lang = _normalize_language(text, language)
    if target_lang != "en":
        return summarize_t5(text, language=target_lang)

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summary = _textrank(parser.document, sentence_count)
    return " ".join(str(s) for s in summary)


def summarize_t5(text: str, language: str = "auto") -> str:
    target_lang = _normalize_language(text, language)
    clipped_text = (text or "").strip()[:4000]

    _ensure_t5_loaded()
    prompt = "Summarize the following legal document in simple English:\n\n" + clipped_text
    inputs = _t5_tok(prompt, return_tensors="pt", truncation=True)
    outputs = _t5.generate(**inputs, max_length=220, num_beams=4, early_stopping=True)
    english_summary = _t5_tok.decode(outputs[0], skip_special_tokens=True)

    if target_lang == "en":
        return english_summary
    return _translate_text(english_summary, target_lang)


def summarize_text(text: str, method: str = "textrank", language: str = "auto"):
    if not (text or "").strip():
        return "Please provide non-empty document text.", "en"

    target_lang = _normalize_language(text, language)
    if method.lower() == "t5":
        return summarize_t5(text, language=target_lang), target_lang
    return summarize_textrank(text, language=target_lang), target_lang
