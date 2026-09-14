# heartcare-ai-service/vector_store.py
"""
Vector Store Module — Pinecone
Handles upserting and querying document chunk embeddings.

Index configuration:
  - Dimension: 768 (firqaaa/indo-sentence-bert-base)
  - Metric: cosine (best for normalized embeddings)
  - Namespace: "heartcare-kms"
"""

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

NAMESPACE = "heartcare-kms"
UPSERT_BATCH_SIZE = 100  # Pinecone recommends batches of 100


def get_pinecone_index(api_key: str, index_name: str):
    """Initialize Pinecone client and return the target index."""
    pc = Pinecone(api_key=api_key)

    # Create index if it doesn't exist
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        logger.info(f"Membuat Pinecone index baru: '{index_name}' ...")
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        logger.info(f"Index '{index_name}' berhasil dibuat.")
    else:
        logger.info(f"Menggunakan index Pinecone yang sudah ada: '{index_name}'")

    return pc.Index(index_name)


def build_vectors(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    document_id: str,
    document_title: str,
) -> List[Dict[str, Any]]:
    """
    Build Pinecone-compatible vector records.
    Each vector:
        {
            "id": "<document_id>_chunk_<n>",
            "values": [float, ...],    # 768-dim embedding
            "metadata": {
                "document_id": str,
                "document_title": str,
                "chunk_index": int,
                "text": str,           # The actual chunk text for retrieval
                "char_count": int,
            }
        }
    """
    vectors = []
    for chunk, embedding in zip(chunks, embeddings):
        vector_id = f"{document_id}_chunk_{chunk['chunk_index']}"
        vectors.append(
            {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "document_id": document_id,
                    "document_title": document_title,
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "char_count": chunk["char_count"],
                },
            }
        )
    return vectors


def upsert_vectors(
    index,
    vectors: List[Dict[str, Any]],
    namespace: str = NAMESPACE,
) -> Dict[str, int]:
    """
    Upsert vectors to Pinecone in batches.
    Returns summary: { "upserted_count": int }
    """
    total_upserted = 0

    for i in range(0, len(vectors), UPSERT_BATCH_SIZE):
        batch = vectors[i : i + UPSERT_BATCH_SIZE]
        result = index.upsert(vectors=batch, namespace=namespace)
        total_upserted += result.get("upserted_count", len(batch))
        logger.info(
            f"Batch {i // UPSERT_BATCH_SIZE + 1}: {len(batch)} vektor diunggah ke Pinecone."
        )

    return {"upserted_count": total_upserted}


def delete_document_vectors(
    index,
    document_id: str,
    namespace: str = NAMESPACE,
) -> None:
    """
    Delete all vectors for a given document_id.
    Used when re-processing an updated document.
    """
    # Pinecone supports delete by metadata filter (requires index type support)
    index.delete(
        filter={"document_id": {"$eq": document_id}},
        namespace=namespace,
    )
    logger.info(f"Semua vektor untuk dokumen '{document_id}' berhasil dihapus.")


def query_similar(
    index,
    query_embedding: List[float],
    top_k: int = 5,
    namespace: str = NAMESPACE,
    document_id_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query Pinecone for semantically similar chunks.
    Optionally filter by document_id.
    Returns list of matches with text metadata.
    """
    filter_dict = {}
    if document_id_filter:
        filter_dict["document_id"] = {"$eq": document_id_filter}

    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=namespace,
        include_metadata=True,
        filter=filter_dict if filter_dict else None,
    )

    return [
        {
            "id": match["id"],
            "score": match["score"],
            "text": match.get("metadata", {}).get("text", ""),
            "document_title": match.get("metadata", {}).get("document_title", ""),
            "chunk_index": match.get("metadata", {}).get("chunk_index", -1),
        }
        for match in result.get("matches", [])
    ]


# ── ALTERNATIVE VECTOR STORE: SUPABASE PGVECTOR ──────────────────────────────
# If you choose Supabase pgvector instead of Pinecone, run this SQL in Supabase:
#
# CREATE EXTENSION IF NOT EXISTS vector;
# CREATE TABLE IF NOT EXISTS document_embeddings (
#     id TEXT PRIMARY KEY,
#     document_id TEXT NOT NULL,
#     document_title TEXT NOT NULL,
#     chunk_index INT NOT NULL,
#     text TEXT NOT NULL,
#     char_count INT NOT NULL,
#     embedding vector(768) NOT NULL,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );
# CREATE INDEX ON document_embeddings USING ivfflat (embedding vector_cosine_ops);

def upsert_vectors_supabase(
    supabase_client,
    vectors: List[Dict[str, Any]],
    table_name: str = "document_embeddings",
) -> Dict[str, int]:
    """
    Upsert vector records into Supabase pgvector table.
    
    Args:
        supabase_client: Initialized supabase.Client instance
        vectors: Output from build_vectors()
        table_name: Name of the PostgreSQL table with pgvector column
    """
    records = []
    for vec in vectors:
        records.append({
            "id": vec["id"],
            "document_id": vec["metadata"]["document_id"],
            "document_title": vec["metadata"]["document_title"],
            "chunk_index": vec["metadata"]["chunk_index"],
            "text": vec["metadata"]["text"],
            "char_count": vec["metadata"]["char_count"],
            "embedding": vec["values"],  # 768-dim list of floats
        })

    total = 0
    # Batch upsert 50 at a time
    for i in range(0, len(records), 50):
        batch = records[i : i + 50]
        supabase_client.table(table_name).upsert(batch).execute()
        total += len(batch)
        logger.info(f"Batch {i // 50 + 1}: {len(batch)} vektor diunggah ke Supabase.")

    return {"upserted_count": total}


def query_similar_supabase(
    supabase_client,
    query_embedding: List[float],
    top_k: int = 5,
    match_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Query Supabase pgvector using the match_documents RPC function:
    
    CREATE OR REPLACE FUNCTION match_documents (
      query_embedding vector(768),
      match_threshold float,
      match_count int
    )
    RETURNS TABLE (
      id text,
      document_title text,
      text text,
      similarity float
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
      RETURN QUERY
      SELECT
        document_embeddings.id,
        document_embeddings.document_title,
        document_embeddings.text,
        1 - (document_embeddings.embedding <=> query_embedding) AS similarity
      FROM document_embeddings
      WHERE 1 - (document_embeddings.embedding <=> query_embedding) > match_threshold
      ORDER BY similarity DESC
      LIMIT match_count;
    END;
    $$;
    """
    response = supabase_client.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": top_k,
        },
    ).execute()
    return response.data or []

