# heartcare-ai-service/rag_engine.py
"""
HeartCare Bot — RAG Engine & Web Search Fallback
Stage 5: Intelligent Medical Retrieval-Augmented Generation

Core Capabilities:
1. IndoSBERT 768D semantic query embedding.
2. Pinecone vector search with relevance threshold checking.
3. Web search fallback (DuckDuckGo / Tavily) when Pinecone similarity is low or empty.
4. "Home-Care First" Indonesian clinical system prompt tailored for elderly patients & caregivers.
5. LLM generation with Groq / OpenAI and safe offline fallback.
"""

import logging
from typing import List, Dict, Any, Optional
from config import settings
from embedder import embed_chunks
from vector_store import get_pinecone_index, query_similar

logger = logging.getLogger(__name__)

# ── Home-Care First Medical System Prompt ──────────────────────────────────────
HOME_CARE_SYSTEM_PROMPT = """Anda adalah HeartCare Bot, asisten perawatan mandiri (home-care) khusus untuk pasien Gagal Jantung (Heart Failure) dan pendamping/keluarga (caregiver) di Indonesia.

PEDOMAN PERILAKU & GAYA BAHASA:
1. Nada Bicara: Sangat hangat, sopan, empatik, menenangkan, dan mudah dipahami oleh lansia. Gunakan sapaan "Bapak/Ibu" atau nama pasien jika tersedia.
2. Struktur Jawaban: Jelas, ringkas, menggunakan poin-poin sederhana (bullet points) agar tidak melelahkan untuk dibaca di layar HP.
3. 4 Pilar Utama Perawatan Mandiri (Home-Care):
   - Penimbangan Berat Badan Rutin: Timbang berat badan setiap pagi (setelah buang air kecil, sebelum sarapan). Ingatkan bahwa kenaikan >2 kg dalam 3 hari menandakan penumpukan cairan (edema).
   - Pembatasan Asupan Cairan: Batasi cairan (air minum, kuah sup, es) sekitar 1.5 - 2 Liter/hari atau sesuai instruksi dokter penanggung jawab.
   - Diet Rendah Garam/Natrium: Batasi garam dapur maksimal 1 sendok teh (<2 gram natrium) per hari, hindari makanan olahan/kaleng/asin.
   - Kepatuhan Minum Obat: Minum obat jantung teratur sesuai resep dan jangan pernah menghentikan obat secara mendadak.
4. Tanda Bahaya (RED FLAGS / Kegawatdaruratan):
   Jika pasien mengeluh sesak napas berat saat istirahat/berbaring, nyeri dada menjalar, bibir membiru, detak jantung sangat cepat dan pusing hebat, atau bengkak kaki yang cepat memburuk:
   -> Berikan instruksi tegas dan darurat untuk SEGERA menghubungi ambulans 119 atau menuju IGD Rumah Sakit terdekat!
5. Disclaimer Wajib:
   Selalu tegaskan bahwa saran ini adalah panduan perawatan mandiri dan bukan pengganti konsultasi, diagnosis, atau resep dari dokter spesialis jantung.

INFORMASI KONTEKS DOKUMEN / PENCARIAN TERBARU:
{context}
"""


# ── Web Search Fallback (DuckDuckGo) ──────────────────────────────────────────
def search_medical_web(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search external web for Indonesian clinical guidelines when Pinecone has no close match.
    Uses DuckDuckGo search.
    """
    results: List[Dict[str, str]] = []
    search_query = f"{query} gagal jantung tata laksana site:kemkes.go.id OR site:inaheart.org OR site:alodokter.com OR site:halodoc.com"

    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            ddg_gen = ddgs.text(search_query, max_results=max_results, region="id-id")
            for item in ddg_gen:
                results.append({
                    "title": item.get("title", "Informasi Kesehatan Web"),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", ""),
                    "type": "web",
                })
        logger.info(f"Web search fallback berhasil: {len(results)} hasil ditemukan.")
    except Exception as e:
        logger.warning(f"DuckDuckGo search error: {e}. Menggunakan fallback manual.")
        # Minimal fallback if network fails
        results.append({
            "title": "Panduan Standar Gagal Jantung (Kemenkes RI)",
            "url": "https://kemkes.go.id",
            "snippet": "Tata laksana gagal jantung menekankan pemantauan berat badan harian, pembatasan natrium <2g/hari, restriksi cairan 1.5-2L, serta kontrol teratur.",
            "type": "web",
        })

    return results


# ── Offline Rule-Based Fallback Generator ─────────────────────────────────────
def generate_offline_fallback(
    message: str,
    patient_name: str,
    context_chunks: List[str],
    source_type: str,
) -> str:
    """
    Provides clinically verified, warm Indonesian response if LLM API key is missing or offline.
    """
    greeting = f"Halo Bapak/Ibu {patient_name}" if patient_name else "Halo Bapak/Ibu"
    lower_msg = message.lower()

    if any(w in lower_msg for w in ["gejala", "tanda", "ciri"]):
        body = (
            f"{greeting},\n\n"
            "Gejala umum gagal jantung yang perlu selalu dipantau di rumah meliputi:\n"
            "1. **Sesak Napas (Dispnea):** Terutama saat beraktivitas atau saat berbaring datar.\n"
            "2. **Bengkak pada Kaki (Edema):** Penumpukan cairan di pergelangan kaki atau tungkai.\n"
            "3. **Kenaikan Berat Badan Cepat:** Kenaikan >2 kg dalam 3 hari menandakan retensi cairan.\n"
            "4. **Mudah Lelah:** Tubuh terasa lemas bahkan saat melakukan aktivitas ringan.\n\n"
            "💡 **Penting:** Jika sesak semakin memberat saat tidur malam atau istirahat, segera periksakan ke dokter Anda."
        )
    elif any(w in lower_msg for w in ["minum", "cairan", "air"]):
        body = (
            f"{greeting},\n\n"
            "Aturan pembatasan cairan untuk pasien gagal jantung:\n"
            "• **Jumlah Maksimal:** Umumnya 1.5 hingga 2 liter per 24 jam (termasuk kuah makanan, jus, dan es).\n"
            "• **Trik Menghadapi Haus:** Basahi bibir dengan es batu kecil atau berkumur dengan air dingin.\n"
            "• **Tujuan:** Mencegah cairan menumpuk di paru-paru dan meringankan kerja pompa jantung Anda."
        )
    elif any(w in lower_msg for w in ["garam", "makan", "diet", "pantangan"]):
        body = (
            f"{greeting},\n\n"
            "Pedoman asupan makanan dan garam (natrium):\n"
            "• **Batasan Garam:** Maksimal 1 sendok teh (<2 gram natrium) per hari.\n"
            "• **Hindari:** Makanan kaleng, daging olahan (sosis/kornet), camilan asin, dan penyedap rasa tinggi garam.\n"
            "• **Pilihan Sehat:** Perbanyak sayuran segar, ikan tanpa garam berlebih, dan buah-buahan segar sesuai anjuran dokter."
        )
    elif any(w in lower_msg for w in ["timbang", "berat badan", "bb"]):
        body = (
            f"{greeting},\n\n"
            "Cara tepat pemantauan berat badan harian:\n"
            "1. Timbang setiap pagi hari setelah buang air kecil dan sebelum sarapan.\n"
            "2. Gunakan timbangan yang sama dan pakaian yang serupa.\n"
            "3. Catat di buku harian. Jika berat badan naik lebih dari 2 kg dalam 3 hari, segera hubungi dokter karena itu tanda penumpukan cairan."
        )
    else:
        ctx_summary = "\n".join([f"• {c[:180]}..." for c in context_chunks[:2]]) if context_chunks else ""
        body = (
            f"{greeting},\n\n"
            "Terima kasih atas pertanyaan Anda seputar kesehatan jantung.\n\n"
            + (f"Berdasarkan pedoman klinis terkait:\n{ctx_summary}\n\n" if ctx_summary else "")
            + "Untuk menjaga kondisi jantung tetap stabil di rumah, selalu ingat untuk:\n"
            "1. Minum obat rutin tepat waktu sesuai jadwal alarm.\n"
            "2. Batasi asupan garam dan cairan harian.\n"
            "3. Timbang berat badan setiap pagi.\n\n"
            "Jika merasakan keluhan yang tidak biasa, jangan ragu untuk berkonsultasi langsung dengan dokter spesialis jantung Anda."
        )

    disclaimer = "\n\n⚠️ *HeartCare Bot adalah asisten mandiri dan bukan pengganti diagnosis dokter spesialis jantung.*"
    return body + disclaimer


# ── LLM Response Generation ──────────────────────────────────────────────────
def call_llm(
    system_prompt: str,
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Call Groq (default) or OpenAI API with the structured prompt.
    """
    messages = [{"role": "system", "content": system_prompt}]

    # Append recent conversation history (last 4 turns)
    if conversation_history:
        for turn in conversation_history[-4:]:
            role = "user" if turn.get("sender") == "user" else "assistant"
            content = turn.get("text", "")
            if content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    # Try Groq API first
    if settings.groq_api_key and settings.groq_api_key != "your_groq_api_key":
        try:
            from groq import Groq
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model=settings.llm_model or "llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=800,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq API error: {e}. Mencoba provider lain...")

    # Try OpenAI API
    if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=800,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")

    raise RuntimeError("Tidak ada API LLM aktif atau kuota habis.")


# ── Main RAG Query Pipeline ───────────────────────────────────────────────────
async def generate_chat_response(
    user_message: str,
    patient_name: Optional[str] = "Pengguna",
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Full RAG Pipeline with Fallback:
    1. Embed query with IndoSBERT 768D.
    2. Query Pinecone vector index.
    3. Check similarity threshold.
    4. If low similarity -> Fallback to Web Search (DuckDuckGo).
    5. Construct Prompt & Generate with LLM (or robust clinical rule generator).
    6. Return response + citation sources.
    """
    patient_display = patient_name or "Pengguna"
    source_type = "rag"
    sources: List[Dict[str, Any]] = []
    context_text = ""
    top_score = 0.0

    # 1. Embed query using IndoSBERT
    try:
        query_vectors = embed_chunks(
            chunks=[user_message],
            model_name=settings.indosbert_model,
            batch_size=1,
            show_progress=False,
        )
        query_embedding = query_vectors[0]
    except Exception as e:
        logger.error(f"IndoSBERT embedding error: {e}")
        query_embedding = None

    # 2. Query Pinecone
    matched_chunks: List[Dict[str, Any]] = []
    if query_embedding:
        try:
            index = get_pinecone_index(
                api_key=settings.pinecone_api_key,
                index_name=settings.pinecone_index_name,
            )
            matches = query_similar(
                index=index,
                query_embedding=query_embedding,
                top_k=3,
            )
            matched_chunks = matches
            if matched_chunks:
                top_score = matched_chunks[0].get("score", 0.0)
                logger.info(f"Pinecone top similarity score: {top_score:.4f}")
        except Exception as e:
            logger.warning(f"Pinecone query gagal/tidak terjangkau: {e}")
            matched_chunks = []

    # 3. Check Relevance Threshold
    threshold = settings.rag_similarity_threshold
    high_confidence = matched_chunks and (top_score >= threshold)

    if high_confidence:
        source_type = "rag"
        context_parts = []
        for idx, m in enumerate(matched_chunks):
            doc_title = m.get("document_title", "Pedoman Klinis KMS")
            chunk_txt = m.get("text", "")
            context_parts.append(f"[Sumber {idx+1}: {doc_title}]\n{chunk_txt}")
            sources.append({
                "title": doc_title,
                "type": "document",
                "score": round(m.get("score", 0.0), 3),
                "snippet": chunk_txt[:160] + "...",
            })
        context_text = "\n\n".join(context_parts)
    else:
        # 4. Fallback to Web Search
        source_type = "web_search"
        logger.info("Similarity score di bawah threshold. Mengaktifkan Web Search Fallback...")
        web_results = search_medical_web(user_message, max_results=3)
        context_parts = []
        for w in web_results:
            context_parts.append(f"[Web: {w['title']}]\n{w['snippet']}")
            sources.append({
                "title": w["title"],
                "url": w.get("url", ""),
                "type": "web",
                "snippet": w.get("snippet", "")[:160] + "...",
            })
        context_text = "\n\n".join(context_parts)

    # 5. Build System Prompt & Call LLM
    system_prompt = HOME_CARE_SYSTEM_PROMPT.format(context=context_text)

    try:
        reply = call_llm(
            system_prompt=system_prompt,
            user_message=f"Pertanyaan dari Pasien ({patient_display}): {user_message}",
            conversation_history=conversation_history,
        )
    except Exception as e:
        logger.warning(f"LLM API call failed ({e}). Menggunakan generator klinis mandiri...")
        source_type = "fallback"
        raw_chunks = [s.get("snippet", "") for s in sources]
        reply = generate_offline_fallback(
            message=user_message,
            patient_name=patient_display,
            context_chunks=raw_chunks,
            source_type=source_type,
        )

    return {
        "reply": reply,
        "sources": sources,
        "source_type": source_type,
        "similarity_score": round(top_score, 3) if top_score else None,
    }
