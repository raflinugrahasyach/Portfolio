# heartcare-ai-service/embedder.py
"""
Embedding Module — IndoSBERT
Model: firqaaa/indo-sentence-bert-base
  - Fine-tuned for Bahasa Indonesia sentence similarity
  - Produces 768-dimensional dense vectors
  - Trained on Indonesian NLI + STS datasets

Singleton pattern: model is loaded once at startup to avoid repeated
disk I/O and model initialization on every request.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)

_MODEL: SentenceTransformer | None = None
EMBEDDING_DIM = 768  # Dimension for firqaaa/indo-sentence-bert-base


def get_model(model_name: str) -> SentenceTransformer:
    """Lazy-load the IndoSBERT model (singleton)."""
    global _MODEL
    if _MODEL is None:
        logger.info(f"Memuat model IndoSBERT: {model_name} ...")
        _MODEL = SentenceTransformer(model_name)
        logger.info(f"Model IndoSBERT berhasil dimuat.")
    return _MODEL


def embed_chunks(
    chunks: List[str],
    model_name: str,
    batch_size: int = 32,
    show_progress: bool = True,
) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks.

    Args:
        chunks: List of text strings to embed.
        model_name: HuggingFace model identifier.
        batch_size: Number of texts per GPU/CPU batch.
        show_progress: Show tqdm progress bar.

    Returns:
        List of float vectors, one per chunk.
    """
    model = get_model(model_name)

    # SentenceTransformer handles batching internally
    embeddings: np.ndarray = model.encode(
        chunks,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,  # Normalize to unit length for cosine similarity
        convert_to_numpy=True,
    )

    # Convert numpy array rows to Python lists for JSON serialization
    return [vec.tolist() for vec in embeddings]
