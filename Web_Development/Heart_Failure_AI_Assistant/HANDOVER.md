# 🫀 HeartCare Bot — Panduan Serah Terima Sistem (Handover Document)

**Proyek:** Chatbot & Aplikasi Pemantauan Mandiri Pasien Gagal Jantung Berbasis RAG, IndoSBERT, & Notifikasi Lokal  
**stakeholder:** Kak Gita & Kak Auletta  
**Versi Sistem:** Production Ready (Stage 1 – Stage 6 Selesai 100%)  
**Tanggal:** September 2026  

---

## 📌 1. Ringkasan Arsitektur Sistem

Sistem **HeartCare Bot** dibangun dengan arsitektur modular terpisah menjadi 3 modul utama:

```mermaid
graph TD
    A[📱 Mobile App - React Native Expo] -->|Local Notifications| B[⏰ 4 Alarm Harian Offline]
    A -->|POST /chat| C[🧠 Python AI Microservice - FastAPI]
    D[💻 Admin Web Panel - Next.js] -->|Upload Dokumen KMS| E[(🗄️ MySQL Database)]
    D -->|POST /process-document| C
    C -->|Semantic Chunks| F[🤖 IndoSBERT 768D Model]
    F -->|Dense Vectors| G[(🌲 Pinecone Vector DB)]
    C -->|Similarity < 0.65 Fallback| H[🌐 DuckDuckGo Web Search]
    C -->|Context + Home-Care Persona| I[⚡ Groq LLaMA 3.3 / OpenAI]
```

### 1. **Mobile Application (`heartcarebot`)**
- **Teknologi:** React Native (Expo SDK 57), TypeScript, Expo Router, Expo Notifications.
- **Fungsi:** 
  - UI/UX ramah lansia (kontras tinggi, font besar >18px, target sentuh luas).
  - 4 Alarm pengingat harian lokal (Timbang BB jam 08:00, Obat jam 08:00, 13:00, 20:00).
  - Antarmuka chat interaktif terhubung langsung ke backend RAG dengan penampil sumber sitasi (📚 Pedoman Klinis / 🌐 Pencarian Web).

### 2. **Admin Web Panel (`heartcare-admin`)**
- **Teknologi:** Next.js (App Router), Tailwind CSS, Prisma ORM, MySQL.
- **Fungsi:** analytics interface upload dokumen pedoman klinis (KMS) dalam format PDF, Word (DOCX), atau TXT. Status pemrosesan otomatis diperbarui secara live (`PENDING` ➔ `PROCESSING` ➔ `INDEXED` / `FAILED`).

### 3. **AI & RAG Microservice (`heartcare-ai-service`)**
- **Teknologi:** Python 3.10+, FastAPI, IndoSBERT (`firqaaa/indo-sentence-bert-base`), LangChain Text Splitters, Pinecone Vector DB, DuckDuckGo Search, Groq API (LLaMA 3.3 70B) / OpenAI.
- **Fungsi:** Ekstraksi teks, chunking semantik Bahasa Indonesia, embedding 768 dimensi, similarity search, threshold relevance check (<0.65 ➔ web search fallback), serta persona klinis *Home-Care First*.

---

## ⚙️ 2. Prasyarat Sistem (Prerequisites)

Pastikan komputer/laptop telah terpasang:
1. **Node.js**: Versi `v20.x` atau `v22.x` (LTS).
2. **Python**: Versi `3.10` atau `3.11` atau `3.12`.
3. **Database MySQL**: MySQL Server 8.0 atau XAMPP MySQL.
4. **Git** & **PowerShell** (Windows) / Terminal (macOS/Linux).
5. **Expo Go** (di HP Android) atau **Android Studio Emulator**.

---

## 🚀 3. Panduan Menjalankan Sistem Secara Lokal

### Langkah 1: Jalankan Database MySQL
Pastikan service MySQL aktif (misal lewat XAMPP Control Panel atau Windows Service). Buat database baru bernama `heartcare_db`:
```sql
CREATE DATABASE IF NOT EXISTS heartcare_db;
```

---

### Langkah 2: Jalankan Admin Web Panel (`heartcare-admin`)
Buka terminal PowerShell baru:

```powershell
cd "heartcare-admin"

# 1. Salin konfigurasi environment
Copy-Item .env.example .env

# Sesuaikan DATABASE_URL di file .env jika menggunakan password root yang berbeda:
# DATABASE_URL="mysql://root:password@localhost:3306/heartcare_db"

# 2. Sinkronkan schema Prisma ke MySQL
npx prisma db push

# 3. Jalankan server Next.js (Port 3000)
npm run dev
```
👉 Buka browser di: `http://localhost:3000`

---

### Langkah 3: Jalankan AI Microservice (`heartcare-ai-service`)
Buka terminal PowerShell kedua:

```powershell
cd "heartcare-ai-service"

# 1. Buat dan aktifkan virtual environment Python
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install seluruh dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Salin konfigurasi environment
Copy-Item .env.example .env

# Masukkan API Key Anda di file .env:
# - PINECONE_API_KEY="..."
# - GROQ_API_KEY="..." (Bisa gratis dari https://console.groq.com)

# 4. Jalankan FastAPI server (Port 8000)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
👉 Buka dokumentasi Swagger API di: `http://localhost:8000/docs`

---

### Langkah 4: Jalankan Mobile App (`heartcarebot`)
Buka terminal PowerShell ketiga:

```powershell
cd "heartcarebot"

# 1. Jalankan Metro bundler Expo
npx expo start
```
- **Di HP Android Fisik:** Scan QR Code menggunakan aplikasi **Expo Go**. (Pastikan HP dan laptop terhubung ke jaringan Wi-Fi yang sama).
- **Di Emulator Android:** Tekan huruf `a` di terminal.

---

## 📦 4. Panduan Kompilasi APK Android (EAS Build)

Untuk menghasilkan file installer `.apk` mandiri yang dapat di-share langsung ke pasien tanpa perlu Expo Go:

### Opsi A: Cloud Build (Direkomendasikan — Menggunakan Server Expo)
```powershell
cd "heartcarebot"

# 1. Install EAS CLI secara global jika belum ada
npm install -g eas-cli

# 2. Login ke akun Expo (daftar gratis di https://expo.dev)
eas login

# 3. Jalankan kompilasi APK profil preview
eas build -p android --profile preview
```
*Tunggu proses build di cloud selesai (sekitar 5-10 menit). Anda akan mendapatkan link download file `.apk` langsung.*

### Opsi B: Local Build (Jika memiliki Android SDK & Java JDK di PC lokal)
```powershell
npx eas build -p android --profile preview --local
```

---

## ☁️ 5. Panduan release Cloud Gratis (Plug-and-Play untuk stakeholder)

Untuk menjadikan sistem sepenuhnya *cloud-hosted* tanpa perlu menjalankan server di laptop stakeholder:

### 1. Deploy AI Microservice ke Render.com (Gratis)
1. Buat akun di [Render.com](https://render.com).
2. Buat **New Web Service** dan hubungkan ke repository GitHub (folder `heartcare-ai-service`).
3. Render akan otomatis membaca konfigurasi `render.yaml` / `Procfile`:
   - **Runtime:** Python 3
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Masukkan **Environment Variables** di analytics interface Render:
   - `PINECONE_API_KEY`: API Key Pinecone Anda
   - `GROQ_API_KEY`: API Key Groq Anda
   - `PINECONE_INDEX_NAME`: `heartcare-docs`
   - `LLM_PROVIDER`: `groq`
5. Setelah status *Live*, Anda akan mendapatkan URL seperti: `https://heartcare-ai-service.onrender.com`.

---

### 2. Deploy Admin Web Panel ke Vercel (Gratis)
1. Buat akun di [Vercel.com](https://vercel.com).
2. Import project dari folder `heartcare-admin`.
3. Masukkan **Environment Variables** di Vercel:
   - `DATABASE_URL`: Connection string MySQL Cloud (contoh dari TiDB Cloud / Aiven / Railway)
   - `AI_SERVICE_URL`: URL Render Anda (e.g. `https://heartcare-ai-service.onrender.com`)
4. Klik **Deploy**. Web admin akan live dan dapat diakses dari mana saja.

---

### 3. Build APK Mobile Final (Tersambung ke Cloud)
1. Buka file `heartcarebot/.env` dan ubah URL API ke URL Render yang sudah aktif:
   ```env
   EXPO_PUBLIC_AI_API_URL="https://heartcare-ai-service.onrender.com"
   ```
2. Jalankan kompilasi APK cloud:
   ```powershell
   cd "heartcarebot"
   eas build -p android --profile preview
   ```
3. Unduh file `.apk` hasil build dan bagikan langsung ke stakeholder/pasien. Aplikasi langsung aktif 24/7 tanpa perlu server lokal.

---

## 🔑 6. Konfigurasi Environment Variables (`.env`)

### 1. `heartcare-admin/.env`
```env
DATABASE_URL="mysql://root:password@localhost:3306/heartcare_db"
AI_SERVICE_URL="https://heartcare-ai-service.onrender.com"
MAX_FILE_SIZE="20971520"
```

### 2. `heartcare-ai-service/.env`
```env
PINECONE_API_KEY="your_pinecone_api_key"
PINECONE_INDEX_NAME="heartcare-docs"
PINECONE_ENVIRONMENT="us-east-1-aws"

LLM_PROVIDER="groq"
GROQ_API_KEY="gsk_your_groq_api_key"
OPENAI_API_KEY="sk-your_openai_api_key"
LLM_MODEL="llama-3.3-70b-versatile"

RAG_SIMILARITY_THRESHOLD="0.65"
INDOSBERT_MODEL="firqaaa/indo-sentence-bert-base"
UPLOAD_DIR="./uploaded_docs"
APP_ENV="production"
```

### 3. `heartcarebot/.env`
```env
EXPO_PUBLIC_AI_API_URL="https://heartcare-ai-service.onrender.com"
```

---

## 🩺 7. Alur Pengujian Fitur Klinis (Verification Checklist)

| No | Fitur | Cara Pengujian | Hasil yang Diharapkan |
|---|---|---|---|
| 1 | **Upload Dokumen KMS** | Buka Admin Panel, drag-and-drop file PDF pedoman jantung, klik "Unggah & Proses AI". | File tersimpan di database, otomatis di-chunk dan divektorisasi ke Pinecone (Status: `Terindeks`). |
| 2 | **Alarm Harian Mandiri** | Buka menu *Jadwal Pengingat* di HP, aktifkan switch toggle. | 4 alarm harian terdaftar di sistem Android (Timbang BB 08:00, Obat 08:00, 13:00, 20:00). |
| 3 | **Chatbot RAG (KMS)** | Tanya: *"Berapa batas minum air dan konsumsi garam?"* | AI menjawab dengan ramah (gaya bahasa lansia) mengutip sumber KMS: max 1.5-2L air dan <2g garam/hari. |
| 4 | **Web Search Fallback** | Tanya topik baru yang belum ada di dokumen KMS. | Similarity score < 0.65 memicu DuckDuckGo search; badge sitasi menampilkan `🌐 Pencarian Web`. |
| 5 | **Deteksi Kegawatdaruratan** | Tanya: *"Dada saya sakit sekali menjalar dan sesak tidak bisa napas."* | AI langsung memprioritaskan peringatan darurat menghubungi **119** atau menuju **IGD terdekat**. |

---

## 🤝 Kontak & Bantuan Teknis
Seluruh kode telah dilengkapi dokumentasi terstruktur, arsitektur modular, penanganan error tingkat tinggi, dan konfigurasi release cloud gratis untuk memudahkan serah terima kepada stakeholder.

*Selamat menggunakan HeartCare Bot!* 💙

