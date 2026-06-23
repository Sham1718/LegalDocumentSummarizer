from fastapi import FastAPI
from pydantic import BaseModel
from rag_core import ask_rag
from summary_core import summarize_text
from explain_core import explain_textrank
from pdfminer.high_level import extract_text as pdf_text
from docx import Document


app = FastAPI(title="Legal Document ML API")

class QuestionRequest(BaseModel):
    question: str
    language: str = "auto"
    top_k: int = 6
    include_explanation: bool = False
    answer_length: str = "medium"  # short | medium | long

class ChunkEvidence(BaseModel):
    chunk_id: str
    distance: float
    text: str

class AnswerResponse(BaseModel):
    answer: str
    explanation: str
    sources: list[str]
    evidence_chunks: list[ChunkEvidence]
    language: str

class SummaryRequest(BaseModel):
    text: str
    method: str = "textrank"  # "textrank" or "t5"
    language: str = "auto"

class SummaryResponse(BaseModel):
    summary: str
    language: str

class ExplainRequest(BaseModel):
    text: str
    language: str = "auto"

class ExplainResponse(BaseModel):
    explanation: list
    language: str

class DocumentProcessRequest(BaseModel):
    path: str
    method: str = "t5"
    language: str = "auto"


@app.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    answer_tokens_map = {"short": 96, "medium": 160, "long": 240}
    answer_tokens = answer_tokens_map.get(req.answer_length.lower(), 160)

    explanation = ""
    if req.include_explanation:
        answer, sources, evidence, resolved_lang, explanation = ask_rag(
            req.question,
            language=req.language,
            top_k=req.top_k,
            return_chunks=True,
            return_explanation=True,
            gen_max_new_tokens=answer_tokens,
        )
    else:
        answer, sources, evidence, resolved_lang = ask_rag(
            req.question,
            language=req.language,
            top_k=req.top_k,
            return_chunks=True,
            gen_max_new_tokens=answer_tokens,
        )
    return {
        "answer": answer,
        "explanation": explanation,
        "sources": sources,
        "evidence_chunks": evidence,
        "language": resolved_lang
    }

@app.post("/summarize", response_model=SummaryResponse)
def summarize(req: SummaryRequest):
    summary, resolved_lang = summarize_text(
        req.text,
        method=req.method,
        language=req.language,
    )
    return {"summary": summary, "language": resolved_lang}

@app.post("/explain-summary", response_model=ExplainResponse)
def explain_summary(req: ExplainRequest):
    explanation, resolved_lang = explain_textrank(req.text, language=req.language)
    return {"explanation": explanation, "language": resolved_lang}

@app.post("/document/process")
def process_document(req: DocumentProcessRequest):
    path = req.path

    text = extract_text(path)

    summary, resolved_lang = summarize_text(
        text,
        method=req.method,
        language=req.language,
    )
    explanation, explain_lang = explain(text, req.language)

    return {
        "summary": summary,
        "language": resolved_lang,
        "explanation": explanation,
        "explanation_language": explain_lang,
    }

def extract_text(path):
    if path.endswith(".pdf"):
        return pdf_text(path)

    if path.endswith(".docx"):
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    raise ValueError("Unsupported file type")

def summarize(text: str) -> str:
    """
    Default summarization for document upload.
    Uses T5 for better quality.
    """
    summary, _ = summarize_text(text, method="t5", language="auto")
    return summary


def explain(text: str, language: str = "auto"):
    """
    Explanation using TextRank-based explainability.
    Returns structured explanation.
    """
    return explain_textrank(text, language=language)


