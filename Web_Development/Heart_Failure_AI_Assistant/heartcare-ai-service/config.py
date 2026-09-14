# heartcare-ai-service/config.py
"""
Application configuration — reads from .env file.
Uses pydantic-settings for type-safe env var loading.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Pinecone
    pinecone_api_key: str = "your_pinecone_api_key"
    pinecone_index_name: str = "heartcare-docs"
    pinecone_environment: str = "us-east-1-aws"

    # Supabase (Optional alternative)
    supabase_url: str = "https://your-project.supabase.co"
    supabase_key: str = "your-supabase-key"

    # IndoSBERT Model
    indosbert_model: str = "firqaaa/indo-sentence-bert-base"

    # LLM & RAG Engine Settings
    llm_provider: str = "groq"  # "groq" | "openai" | "fallback"
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    llm_model: str = "llama-3.3-70b-versatile"
    
    # RAG Similarity Threshold (Cosine score: 0.0 - 1.0)
    # If Pinecone top match is below this threshold, fallback to Web Search
    rag_similarity_threshold: float = 0.65

    # Storage
    upload_dir: str = "./uploaded_docs"

    # App
    app_env: str = "development"


settings = Settings()
