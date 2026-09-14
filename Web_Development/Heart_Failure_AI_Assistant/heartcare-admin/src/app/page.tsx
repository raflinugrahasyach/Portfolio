"use client";
// src/app/page.tsx
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Admin Panel — Modern Clinical Guideline Management Dashboard
// Designed for Healthcare Researchers & Doctors (Kak Gita & Kak Auletta)
// ─────────────────────────────────────────────────────────────────────────────

import { useState, useEffect, useCallback, useRef, DragEvent, ChangeEvent } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────
type DocumentStatus = "PENDING" | "PROCESSING" | "INDEXED" | "FAILED";

interface DocumentRecord {
  id: string;
  title: string;
  filename: string;
  fileSize: number;
  mimeType: string;
  uploadDate: string;
  status: DocumentStatus;
  chunksCount?: number;
  vectorCount?: number;
  errorMsg?: string;
}

// ── Formatters ────────────────────────────────────────────────────────────────
function formatBytes(bytes: number): string {
  if (!bytes || isNaN(bytes)) return "0 B";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function getFileBadge(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (ext === "pdf") {
    return {
      icon: "📕",
      tag: "PDF",
      bg: "bg-red-500/10",
      border: "border-red-500/20",
      text: "text-red-400",
    };
  }
  if (ext === "docx" || ext === "doc") {
    return {
      icon: "📘",
      tag: "DOCX",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
      text: "text-blue-400",
    };
  }
  return {
    icon: "📄",
    tag: "TXT",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
    text: "text-emerald-400",
  };
}

// ── Status Configuration ──────────────────────────────────────────────────────
const STATUS_CONFIG: Record<
  DocumentStatus,
  { label: string; badgeClass: string; dotClass: string }
> = {
  PENDING: {
    label: "Menunggu AI",
    badgeClass: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    dotClass: "bg-amber-400",
  },
  PROCESSING: {
    label: "Memproses...",
    badgeClass: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    dotClass: "bg-blue-400 animate-ping",
  },
  INDEXED: {
    label: "Terindeks Vektor",
    badgeClass: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    dotClass: "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]",
  },
  FAILED: {
    label: "Gagal Proses",
    badgeClass: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    dotClass: "bg-rose-400",
  },
};

export default function AdminDashboard() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [retryingId, setRetryingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: "success" | "error" | "info" } | null>(
    null
  );

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Show Toast Notification ─────────────────────────────────────────────────
  const showToast = useCallback((msg: string, type: "success" | "error" | "info" = "info") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4500);
  }, []);

  // ── Fetch Documents from API ────────────────────────────────────────────────
  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch("/api/upload");
      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.error || "Gagal memuat dokumen.");
      }
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (err: any) {
      console.error("[Fetch Documents Error]:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Poll list every 6 seconds to track real-time AI vectorization progress
  useEffect(() => {
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 6000);
    return () => clearInterval(interval);
  }, [fetchDocuments]);

  // ── File Handlers ───────────────────────────────────────────────────────────
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!uploadTitle) {
        const cleanName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
        setUploadTitle(cleanName.charAt(0).toUpperCase() + cleanName.slice(1));
      }
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!uploadTitle) {
        const cleanName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
        setUploadTitle(cleanName.charAt(0).toUpperCase() + cleanName.slice(1));
      }
    }
  };

  // ── Upload Document ─────────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!selectedFile) {
      showToast("Pilih file dokumen (.pdf, .docx, .txt) terlebih dahulu.", "error");
      return;
    }
    if (!uploadTitle.trim() || uploadTitle.trim().length < 3) {
      showToast("Judul dokumen wajib diisi (minimal 3 karakter).", "error");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("title", uploadTitle.trim());

      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || "Gagal mengunggah file ke server.");
      }

      showToast(`✅ ${data.message || "Dokumen berhasil diunggah!"}`, "success");
      setSelectedFile(null);
      setUploadTitle("");
      if (fileInputRef.current) fileInputRef.current.value = "";
      await fetchDocuments();
    } catch (err: any) {
      console.error("[Upload Error]:", err);
      showToast(`❌ ${err?.message || "Terjadi kendala saat mengunggah."}`, "error");
    } finally {
      setUploading(false);
    }
  };

  // ── Retry AI Vectorization ──────────────────────────────────────────────────
  const handleRetry = async (docId: string, title: string) => {
    setRetryingId(docId);
    try {
      const res = await fetch("/api/upload", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: docId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Gagal mengulang proses.");
      showToast(`🔄 Memproses ulang vektor untuk "${title}"...`, "info");
      await fetchDocuments();
    } catch (err: any) {
      showToast(`❌ ${err?.message || "Gagal mengulang proses."}`, "error");
    } finally {
      setRetryingId(null);
    }
  };

  // ── Delete Document ─────────────────────────────────────────────────────────
  const handleDelete = async (docId: string, title: string) => {
    if (!confirm(`Apakah Anda yakin ingin menghapus dokumen "${title}"?`)) return;

    setDeletingId(docId);
    try {
      const res = await fetch(`/api/upload?id=${docId}`, { method: "DELETE" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Gagal menghapus.");
      showToast(`🗑️ Dokumen "${title}" berhasil dihapus.`, "success");
      await fetchDocuments();
    } catch (err: any) {
      showToast(`❌ ${err?.message || "Gagal menghapus dokumen."}`, "error");
    } finally {
      setDeletingId(null);
    }
  };

  // ── Statistical Summary ─────────────────────────────────────────────────────
  const stats = {
    total: documents.length,
    indexed: documents.filter((d) => d.status === "INDEXED").length,
    processing: documents.filter((d) => d.status === "PROCESSING").length,
    failed: documents.filter((d) => d.status === "FAILED").length,
    totalVectors: documents.reduce((acc, curr) => acc + (curr.vectorCount || 0), 0),
  };

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* ── Toast Notification Bar ── */}
      {toast && (
        <div
          className={`fixed top-6 right-6 z-50 flex items-center gap-3 px-5 py-4 rounded-2xl shadow-2xl border text-sm font-medium backdrop-blur-xl transition-all duration-300 animate-in fade-in slide-in-from-top-4 ${
            toast.type === "success"
              ? "bg-emerald-950/90 text-emerald-200 border-emerald-500/40 shadow-emerald-950/50"
              : toast.type === "error"
              ? "bg-rose-950/90 text-rose-200 border-rose-500/40 shadow-rose-950/50"
              : "bg-blue-950/90 text-blue-200 border-blue-500/40 shadow-blue-950/50"
          }`}
        >
          <span>{toast.msg}</span>
          <button
            onClick={() => setToast(null)}
            className="ml-2 text-xs opacity-60 hover:opacity-100 transition"
          >
            ✕
          </button>
        </div>
      )}

      {/* ── Header Navigation ── */}
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#070B14]/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-xl shadow-lg shadow-blue-600/20">
              🫀
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-lg text-white tracking-tight">HeartCare Admin</h1>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  RAG KMS v2.0
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Pusat Manajemen Dokumen Pedoman Gagal Jantung
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Sistem Aktif (MySQL + IndoSBERT)
            </div>
          </div>
        </div>
      </header>

      {/* ── Main Container ── */}
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-10">
        {/* Title Hero */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-slate-800/40">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
              Basis Pengetahuan Medis
            </h2>
            <p className="mt-2 text-base text-slate-400 max-w-2xl">
              Kelola dokumen pedoman klinis (*KMS*) yang menjadi acuan jawaban chatbot AI untuk
              pasien gagal jantung. Dokumen otomatis di-vektorisasi ke Pinecone.
            </p>
          </div>
          <div className="text-xs text-slate-500 flex items-center gap-2">
            <span>Model:</span>
            <code className="bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800 text-blue-400">
              IndoSBERT 768D (Dense Retrieval)
            </code>
          </div>
        </div>

        {/* ── Metric Cards ── */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Total Dokumen
            </div>
            <div className="text-3xl font-black text-white">{stats.total}</div>
            <div className="text-xs text-slate-500 mt-1">Pedoman tersimpan</div>
          </div>

          <div className="bg-slate-900/60 border border-emerald-900/40 rounded-2xl p-5 hover:border-emerald-700/50 transition">
            <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2">
              Terindeks AI
            </div>
            <div className="text-3xl font-black text-emerald-400">{stats.indexed}</div>
            <div className="text-xs text-emerald-500/70 mt-1">Siap dijawab bot</div>
          </div>

          <div className="bg-slate-900/60 border border-blue-900/40 rounded-2xl p-5 hover:border-blue-700/50 transition">
            <div className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2">
              Total Vektor
            </div>
            <div className="text-3xl font-black text-blue-400">{stats.totalVectors}</div>
            <div className="text-xs text-blue-500/70 mt-1">Chunk di Pinecone</div>
          </div>

          <div className="bg-slate-900/60 border border-amber-900/40 rounded-2xl p-5 hover:border-amber-700/50 transition">
            <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
              Memproses
            </div>
            <div className="text-3xl font-black text-amber-400">{stats.processing}</div>
            <div className="text-xs text-amber-500/70 mt-1">Sedang di-chunk</div>
          </div>

          <div className="bg-slate-900/60 border border-rose-900/40 rounded-2xl p-5 hover:border-rose-700/50 transition">
            <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2">
              Kendala / Gagal
            </div>
            <div className="text-3xl font-black text-rose-400">{stats.failed}</div>
            <div className="text-xs text-rose-500/70 mt-1">Perlu diulang</div>
          </div>
        </div>

        {/* ── Document Upload Box ── */}
        <section className="bg-gradient-to-b from-slate-900/80 to-slate-900/40 border border-slate-800 rounded-3xl p-8 shadow-xl shadow-black/20">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-2.5 h-7 rounded-full bg-blue-500" />
            <h3 className="text-xl font-bold text-white tracking-tight">
              Unggah Pedoman Medis Baru
            </h3>
          </div>

          {/* Drag & Drop Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-10 flex flex-col items-center justify-center transition-all duration-300 ${
              isDragOver
                ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                : selectedFile
                ? "border-emerald-500/40 bg-emerald-500/5"
                : "border-slate-700/80 hover:border-slate-600 bg-slate-950/40 hover:bg-slate-950/70"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileChange}
            />

            {selectedFile ? (
              <div className="flex flex-col items-center gap-3 text-center">
                <span className="text-5xl drop-shadow-md">{getFileBadge(selectedFile.name).icon}</span>
                <div>
                  <div className="flex items-center justify-center gap-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded font-bold border ${
                        getFileBadge(selectedFile.name).bg
                      } ${getFileBadge(selectedFile.name).border} ${
                        getFileBadge(selectedFile.name).text
                      }`}
                    >
                      {getFileBadge(selectedFile.name).tag}
                    </span>
                    <p className="font-semibold text-white text-base">{selectedFile.name}</p>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{formatBytes(selectedFile.size)}</p>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }}
                  className="mt-2 text-xs font-semibold text-rose-400 hover:text-rose-300 px-3.5 py-1.5 rounded-full bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 transition"
                >
                  ✕ Batalkan Pilihan
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center text-center gap-3">
                <div className="w-16 h-16 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-3xl mb-1 text-blue-400">
                  📤
                </div>
                <div>
                  <p className="text-base font-semibold text-slate-200">
                    Tarik & Lepas file dokumen di sini, atau{" "}
                    <span className="text-blue-400 underline underline-offset-4">klik untuk memilih</span>
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Format didukung: <strong>PDF</strong>, <strong>Word (.docx)</strong>, atau{" "}
                    <strong>TXT</strong> (Maksimal 20 MB)
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Title input & Submit Button */}
          <div className="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-4 mt-6">
            <div className="relative">
              <input
                type="text"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="Masukkan judul pedoman (contoh: Pedoman Gagal Jantung PERKI 2024)"
                className="w-full h-13 px-5 rounded-xl bg-slate-950/80 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
                onKeyDown={(e) => e.key === "Enter" && handleUpload()}
              />
            </div>

            <button
              onClick={handleUpload}
              disabled={uploading || !selectedFile}
              className="h-13 px-8 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:from-blue-600 disabled:hover:to-indigo-600 transition-all shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2.5 min-w-[180px]"
            >
              {uploading ? (
                <>
                  <svg className="animate-spin w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <span>Mengunggah...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Unggah & Proses AI</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* ── Document List Table ── */}
        <section className="bg-slate-900/60 border border-slate-800/80 rounded-3xl overflow-hidden shadow-xl">
          <div className="px-8 py-5 border-b border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-7 rounded-full bg-emerald-500" />
              <div>
                <h3 className="text-xl font-bold text-white tracking-tight">
                  Daftar Pedoman Terdaftar
                </h3>
                <p className="text-xs text-slate-400">
                  Status otomatis diperbarui secara live tiap 6 detik
                </p>
              </div>
            </div>

            <button
              onClick={fetchDocuments}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800/80 hover:bg-slate-750 text-slate-300 border border-slate-700/60 transition"
            >
              <span>🔄</span>
              <span>Segarkan Data</span>
            </button>
          </div>

          {loading ? (
            <div className="py-24 flex flex-col items-center justify-center gap-3 text-slate-400">
              <svg className="animate-spin w-8 h-8 text-blue-500" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              <p className="text-sm font-medium">Memuat basis pengetahuan...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="py-24 flex flex-col items-center justify-center text-center gap-3 text-slate-500">
              <span className="text-5xl">📚</span>
              <p className="text-base font-semibold text-slate-300">Belum ada dokumen pedoman klinis</p>
              <p className="text-xs text-slate-500 max-w-sm">
                Silakan unggah dokumen pedoman tata laksana gagal jantung pertama Anda di atas untuk
                mulai mengindeks pengetahuan AI.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    <th className="px-6 py-4">Dokumen</th>
                    <th className="px-6 py-4">Ukuran</th>
                    <th className="px-6 py-4">Tanggal Unggah</th>
                    <th className="px-6 py-4">Status AI</th>
                    <th className="px-6 py-4">Metrik Vektor</th>
                    <th className="px-6 py-4 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {documents.map((doc) => {
                    const badge = getFileBadge(doc.filename);
                    const statusCfg = STATUS_CONFIG[doc.status] || STATUS_CONFIG.PENDING;

                    return (
                      <tr
                        key={doc.id}
                        className="hover:bg-slate-800/20 transition-colors group"
                      >
                        {/* Title & Filename */}
                        <td className="px-6 py-4.5">
                          <div className="flex items-center gap-3.5">
                            <div
                              className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg border shrink-0 ${badge.bg} ${badge.border}`}
                            >
                              {badge.icon}
                            </div>
                            <div className="min-w-0">
                              <p className="font-semibold text-white truncate max-w-xs sm:max-w-md">
                                {doc.title}
                              </p>
                              <p className="text-xs text-slate-400 truncate max-w-xs">
                                {doc.filename}
                              </p>
                            </div>
                          </div>
                        </td>

                        {/* File Size */}
                        <td className="px-6 py-4.5 text-slate-300 text-xs font-medium">
                          {formatBytes(doc.fileSize)}
                        </td>

                        {/* Upload Date */}
                        <td className="px-6 py-4.5 text-slate-400 text-xs">
                          {formatDate(doc.uploadDate)}
                        </td>

                        {/* Status Badge */}
                        <td className="px-6 py-4.5">
                          <div
                            className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border ${statusCfg.badgeClass}`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full ${statusCfg.dotClass}`} />
                            <span>{statusCfg.label}</span>
                          </div>
                        </td>

                        {/* Metrics or Error tooltip */}
                        <td className="px-6 py-4.5 text-xs">
                          {doc.status === "INDEXED" ? (
                            <div className="space-y-0.5">
                              <span className="text-slate-200 font-semibold">
                                {doc.chunksCount ?? 0} Chunk
                              </span>
                              <span className="text-slate-500 block text-[11px]">
                                {doc.vectorCount ?? 0} Vektor Pinecone
                              </span>
                            </div>
                          ) : doc.status === "FAILED" ? (
                            <div
                              className="text-rose-400 text-[11px] max-w-[180px] truncate"
                              title={doc.errorMsg || "Gagal memproses"}
                            >
                              ⚠️ {doc.errorMsg || "Gagal memproses"}
                            </div>
                          ) : doc.status === "PROCESSING" ? (
                            <span className="text-blue-400 text-[11px]">Ekstraksi teks...</span>
                          ) : (
                            <span className="text-slate-500 text-[11px]">—</span>
                          )}
                        </td>

                        {/* Action Buttons */}
                        <td className="px-6 py-4.5 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {doc.status === "FAILED" && (
                              <button
                                onClick={() => handleRetry(doc.id, doc.title)}
                                disabled={retryingId === doc.id}
                                className="px-2.5 py-1 rounded-lg text-xs font-semibold text-blue-400 hover:text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 transition disabled:opacity-50"
                                title="Ulangi Vektorisasi AI"
                              >
                                {retryingId === doc.id ? "..." : "🔄 Coba Lagi"}
                              </button>
                            )}

                            <button
                              onClick={() => handleDelete(doc.id, doc.title)}
                              disabled={deletingId === doc.id}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition disabled:opacity-50"
                              title="Hapus Dokumen"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
