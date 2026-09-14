# heartcare-ai-service/README.md
# HeartCare AI Microservice — Stage 4

## Tech Stack
- **FastAPI** — REST API framework
- **IndoSBERT** (`firqaaa/indo-sentence-bert-base`) — 768D Indonesian sentence embeddings
- **LangChain** — Semantic text chunking
- **Pinecone** — Vector database for similarity search
- **pypdf + python-docx** — Document parsing

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows
# source venv/bin/activate       # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
copy .env.example .env
# Fill in PINECONE_API_KEY in .env

# 4. Run the service
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint                | Description                          |
|--------|------------------------|--------------------------------------|
| GET    | /health                | Health check                         |
| POST   | /process-document      | Process file by server path          |
| POST   | /upload-and-process    | Upload + process in one step (test)  |
| GET    | /docs                  | Swagger UI                           |

## IndoSBERT Model Notes
- Model: `firqaaa/indo-sentence-bert-base`
- Dimension: **768**
- Trained on Indonesian NLI + STS datasets
- Use `normalize_embeddings=True` (cosine similarity)
- First run will download ~400MB model from HuggingFace

## Pinecone Configuration
- Create a free index at https://app.pinecone.io
- Dimension: **768**, Metric: **cosine**
- Serverless (AWS us-east-1) recommended for free tier

## Processing Pipeline
```
PDF/DOCX/TXT
  → document_parser.py  (extract raw text)
  → chunker.py          (semantic splitting, 512 chars, 64 overlap)
  → embedder.py         (IndoSBERT, 768D vectors)
  → vector_store.py     (upsert to Pinecone)
```
