# heartcare-ai-service/main.py
"""
HeartCare AI Microservice — FastAPI
Stage 4 & 5: Document Vectorization & Chatbot RAG Engine

Endpoints:
  POST /chat               — Chatbot RAG query with IndoSBERT + Pinecone + Web Search fallback
  POST /process-document   — Parse, chunk, embed, and upsert a document from Next.js
  POST /upload-and-process — Direct file upload and vectorization testing
  GET  /health             — Health check endpoint
  GET  /docs               — Swagger UI
"""

import os
import uuid
import logging
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from document_parser import parse_document
from chunker import chunk_text
from embedder import embed_chunks
from vector_store import get_pinecone_index, build_vectors, upsert_vectors
from rag_engine import generate_chat_response

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="HeartCare AI Microservice",
    description=(
        "Layanan AI untuk pemrosesan dokumen klinis Gagal Jantung (KMS) "
        "dan RAG Chatbot dengan IndoSBERT, Pinecone, serta Web Search Fallback."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration — allows Next.js admin & Expo mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., description="Pesan pertanyaan dari pasien atau caregiver")
    patient_name: Optional[str] = Field(default="Pengguna", description="Nama pasien untuk personalisasi")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Riwayat percakapan sebelumnya"
    )


class SourceCitation(BaseModel):
    title: str
    type: str  # "document" | "web"
    url: Optional[str] = None
    snippet: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    reply: str
    sources: List[SourceCitation]
    source_type: str  # "rag" | "web_search" | "fallback"
    similarity_score: Optional[float] = None


class ProcessByPathRequest(BaseModel):
    file_path: str
    document_title: str
    document_id: Optional[str] = None


class ProcessingResult(BaseModel):
    document_id: str
    document_title: str
    file_path: str
    total_chars: int
    total_chunks: int
    upserted_count: int
    status: str
    message: str


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root_check():
    return {
        "status": "ok",
        "service": "HeartCare AI Microservice",
        "message": "HeartCare AI Microservice is active and ready.",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "service": "HeartCare AI Microservice",
        "model": settings.indosbert_model,
        "llm_provider": settings.llm_provider,
        "environment": settings.app_env,
    }


# ── Endpoint: Chatbot RAG Engine (Stage 5) ────────────────────────────────────
@app.post("/chat", response_model=ChatResponse, tags=["Chatbot RAG"])
async def chat_endpoint(request: ChatRequest):
    """
    RAG Chatbot Endpoint:
    1. Embeds user question via IndoSBERT (768D).
    2. Queries Pinecone vector index for KMS clinical guideline chunks.
    3. If similarity < threshold, triggers DuckDuckGo search fallback.
    4. Generates empathetic, Indonesian Home-Care response using LLM (or robust clinical generator).
    """
    try:
        result = await generate_chat_response(
            user_message=request.message,
            patient_name=request.patient_name,
            conversation_history=request.conversation_history,
        )
        return ChatResponse(
            reply=result["reply"],
            sources=[SourceCitation(**s) for s in result["sources"]],
            source_type=result["source_type"],
            similarity_score=result.get("similarity_score"),
        )
    except Exception as e:
        logger.exception(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat memproses jawaban AI: {str(e)}",
        )


# ── Core Document Vectorization Pipeline ──────────────────────────────────────
async def _process_document_pipeline(
    file_path: str,
    document_title: str,
    document_id: str,
) -> ProcessingResult:
    """Full pipeline: parse → semantic chunking → IndoSBERT embed → Pinecone upsert."""
    # 1. Parse document to raw text
    logger.info(f"[{document_id}] Parsing dokumen: {file_path}")
    raw_text = parse_document(file_path)
    total_chars = len(raw_text)
    logger.info(f"[{document_id}] Teks berhasil diekstrak: {total_chars} karakter")

    # 2. Semantic chunking
    logger.info(f"[{document_id}] Melakukan semantic chunking ...")
    chunks = chunk_text(raw_text, document_title=document_title)
    total_chunks = len(chunks)
    logger.info(f"[{document_id}] {total_chunks} chunk dihasilkan.")

    if total_chunks == 0:
        raise ValueError("Dokumen tidak menghasilkan chunk yang valid setelah diparsing.")

    # 3. Generate IndoSBERT embeddings
    logger.info(f"[{document_id}] Membuat embedding IndoSBERT untuk {total_chunks} chunk ...")
    chunk_texts = [c["text"] for c in chunks]
    embeddings = embed_chunks(
        chunks=chunk_texts,
        model_name=settings.indosbert_model,
        batch_size=32,
        show_progress=False,
    )
    logger.info(f"[{document_id}] Embedding selesai. Dimensi: {len(embeddings[0])}D")

    # 4. Build vector records
    vectors = build_vectors(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        document_title=document_title,
    )

    # 5. Upsert to Pinecone
    logger.info(f"[{document_id}] Mengunggah {len(vectors)} vektor ke Pinecone ...")
    index = get_pinecone_index(
        api_key=settings.pinecone_api_key,
        index_name=settings.pinecone_index_name,
    )
    upsert_result = upsert_vectors(index=index, vectors=vectors)
    upserted_count = upsert_result["upserted_count"]
    logger.info(f"[{document_id}] Selesai. {upserted_count} vektor tersimpan di Pinecone.")

    return ProcessingResult(
        document_id=document_id,
        document_title=document_title,
        file_path=file_path,
        total_chars=total_chars,
        total_chunks=total_chunks,
        upserted_count=upserted_count,
        status="success",
        message=(
            f"Dokumen '{document_title}' berhasil diproses: "
            f"{total_chunks} chunk, {upserted_count} vektor tersimpan di Pinecone."
        ),
    )


# ── Endpoint: Process by file path (Next.js admin upload) ─────────────────────
@app.post("/process-document", response_model=ProcessingResult, tags=["Pipeline"])
async def process_document_by_path(request: ProcessByPathRequest):
    """Receive file path from Next.js, parse, chunk, embed, and upsert."""
    document_id = request.document_id or str(uuid.uuid4())

    try:
        result = await _process_document_pipeline(
            file_path=request.file_path,
            document_title=request.document_title,
            document_id=document_id,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"[{document_id}] Pipeline gagal: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memproses dokumen: {str(e)}",
        )


# ── Endpoint: Upload + Process directly ───────────────────────────────────────
@app.post("/upload-and-process", response_model=ProcessingResult, tags=["Pipeline"])
async def upload_and_process(
    file: UploadFile = File(..., description="PDF, DOCX, atau TXT"),
    document_title: str = Form(..., description="Judul dokumen (e.g. 'Pedoman Gagal Jantung 2024')"),
):
    """Direct file upload and vectorization testing endpoint."""
    allowed_extensions = {".pdf", ".docx", ".txt"}
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"Tipe file '{file_ext}' tidak didukung. Gunakan: {allowed_extensions}",
        )

    document_id = str(uuid.uuid4())
    saved_path = os.path.join(settings.upload_dir, f"{document_id}{file_ext}")

    try:
        with open(saved_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"[{document_id}] File disimpan: {saved_path}")
    finally:
        file.file.close()

    try:
        result = await _process_document_pipeline(
            file_path=saved_path,
            document_title=document_title,
            document_id=document_id,
        )
        return result
    except Exception as e:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
