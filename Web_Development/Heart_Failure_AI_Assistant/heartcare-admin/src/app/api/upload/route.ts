// src/app/api/upload/route.ts
// ─────────────────────────────────────────────────────────────────────────────
// HeartCare Admin — Document Upload & Management API Route
// Handles:
//   - POST: Upload new file, save to disk, record in MySQL, trigger AI pipeline
//   - GET: List all documents with real-time indexing status
//   - DELETE: Remove document record and file from disk
//   - PATCH: Retry AI vectorization pipeline for failed/pending documents
// ─────────────────────────────────────────────────────────────────────────────

import { NextRequest, NextResponse } from "next/server";
import { writeFile, mkdir, unlink, readFile } from "fs/promises";
import { join, extname } from "path";
import { randomUUID } from "crypto";
import { prisma } from "@/lib/prisma";

const ALLOWED_EXTENSIONS = new Set([".pdf", ".docx", ".txt"]);
const MAX_FILE_SIZE = parseInt(process.env.MAX_FILE_SIZE ?? "20971520", 10); // 20 MB default
const UPLOAD_DIR = join(process.cwd(), "public", "uploads");

// ── POST /api/upload ──────────────────────────────────────────────────────────
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File | null;
    const title = (formData.get("title") as string | null)?.trim();

    // ── Validation ────────────────────────────────────────────────────────────
    if (!file) {
      return NextResponse.json(
        { error: "File dokumen wajib dipilih sebelum mengunggah." },
        { status: 400 }
      );
    }

    if (!title || title.length < 3) {
      return NextResponse.json(
        { error: "Judul dokumen wajib diisi (minimal 3 karakter)." },
        { status: 400 }
      );
    }

    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: `Ukuran file melebihi batas (${(MAX_FILE_SIZE / 1024 / 1024).toFixed(0)} MB).` },
        { status: 413 }
      );
    }

    const ext = extname(file.name).toLowerCase();
    if (!ALLOWED_EXTENSIONS.has(ext)) {
      return NextResponse.json(
        { error: `Format file '${ext}' tidak didukung. Silakan gunakan format PDF, DOCX, atau TXT.` },
        { status: 415 }
      );
    }

    // ── Save file to local disk ───────────────────────────────────────────────
    await mkdir(UPLOAD_DIR, { recursive: true });

    const documentId = randomUUID();
    const savedFilename = `${documentId}${ext}`;
    const savedPath = join(UPLOAD_DIR, savedFilename);

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    await writeFile(savedPath, buffer);

    // ── Create Document record in MySQL ───────────────────────────────────────
    let document;
    try {
      document = await prisma.document.create({
        data: {
          id: documentId,
          title,
          filename: file.name,
          fileSize: file.size,
          mimeType: file.type || "application/octet-stream",
          storagePath: `/uploads/${savedFilename}`,
          status: "PENDING",
        },
      });
    } catch (dbError: any) {
      console.error("[Database Error] Gagal menyimpan ke MySQL:", dbError);
      // Clean up uploaded file if DB insert fails
      await unlink(savedPath).catch(() => {});
      return NextResponse.json(
        {
          error: `Gagal menyimpan metadata ke database: ${dbError?.message || "Pastikan MySQL port 3306 aktif."}`,
        },
        { status: 500 }
      );
    }

    // ── Trigger AI pipeline (asynchronous non-blocking) ───────────────────────
    const aiServiceUrl = process.env.AI_SERVICE_URL ?? "http://localhost:8000";
    triggerAIProcessing(aiServiceUrl, savedPath, title, documentId, buffer, file.name).catch(
      (err) => {
        console.warn(`[AI Pipeline Background] Notifikasi untuk ${documentId}:`, err?.message || err);
      }
    );

    return NextResponse.json(
      {
        success: true,
        document,
        message: `Dokumen '${title}' berhasil diunggah! AI sedang melakukan chunking dan pengindeksan vektor.`,
      },
      { status: 201 }
    );
  } catch (error: any) {
    console.error("[/api/upload POST Critical Error]:", error);
    return NextResponse.json(
      {
        error: error?.message || "Terjadi kendala pada server saat memproses unggahan file.",
      },
      { status: 500 }
    );
  }
}

// ── GET /api/upload — List all documents ─────────────────────────────────────
export async function GET() {
  try {
    const documents = await prisma.document.findMany({
      orderBy: { uploadDate: "desc" },
      select: {
        id: true,
        title: true,
        filename: true,
        fileSize: true,
        mimeType: true,
        uploadDate: true,
        status: true,
        chunksCount: true,
        vectorCount: true,
        errorMsg: true,
      },
    });
    return NextResponse.json({ documents });
  } catch (error: any) {
    console.error("[/api/upload GET] Error fetching documents:", error);
    return NextResponse.json(
      { error: `Gagal memuat daftar dokumen: ${error?.message || "Koneksi database terputus."}` },
      { status: 500 }
    );
  }
}

// ── DELETE /api/upload — Delete a document ───────────────────────────────────
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");

    if (!id) {
      return NextResponse.json({ error: "Parameter ID dokumen wajib diberikan." }, { status: 400 });
    }

    const doc = await prisma.document.findUnique({ where: { id } });
    if (!doc) {
      return NextResponse.json({ error: "Dokumen tidak ditemukan." }, { status: 404 });
    }

    // Delete file from disk
    const fullPath = join(process.cwd(), "public", doc.storagePath);
    await unlink(fullPath).catch(() => {});

    // Delete record from DB
    await prisma.document.delete({ where: { id } });

    return NextResponse.json({
      success: true,
      message: `Dokumen '${doc.title}' berhasil dihapus.`,
    });
  } catch (error: any) {
    console.error("[/api/upload DELETE] Error:", error);
    return NextResponse.json(
      { error: `Gagal menghapus dokumen: ${error?.message || "Kesalahan internal."}` },
      { status: 500 }
    );
  }
}

// ── PATCH /api/upload — Retry AI vectorization ──────────────────────────────
export async function PATCH(request: NextRequest) {
  try {
    const { id } = await request.json();
    if (!id) {
      return NextResponse.json({ error: "Parameter ID dokumen diperlukan." }, { status: 400 });
    }

    const doc = await prisma.document.findUnique({ where: { id } });
    if (!doc) {
      return NextResponse.json({ error: "Dokumen tidak ditemukan." }, { status: 404 });
    }

    const savedPath = join(process.cwd(), "public", doc.storagePath);
    const aiServiceUrl = process.env.AI_SERVICE_URL ?? "http://localhost:8000";

    const buffer = await readFile(savedPath).catch(() => null);

    triggerAIProcessing(
      aiServiceUrl,
      savedPath,
      doc.title,
      doc.id,
      buffer ? Buffer.from(buffer) : undefined,
      doc.filename
    ).catch((err) => {
      console.warn(`[AI Retry] Error:`, err);
    });

    return NextResponse.json({
      success: true,
      message: `Proses vektorisasi AI untuk '${doc.title}' telah dijalankan kembali.`,
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: `Gagal memproses ulang: ${error?.message || "Kesalahan internal."}` },
      { status: 500 }
    );
  }
}

// ── Helper: Asynchronous AI Pipeline Processor ───────────────────────────────
async function triggerAIProcessing(
  aiServiceUrl: string,
  filePath: string,
  documentTitle: string,
  documentId: string,
  fileBuffer?: Buffer,
  originalFilename?: string
): Promise<void> {
  // 1. Update status to PROCESSING in MySQL
  await prisma.document
    .update({
      where: { id: documentId },
      data: { status: "PROCESSING", errorMsg: null },
    })
    .catch(() => {});

  try {
    // 2. Try JSON process-document endpoint (fast local path)
    let aiResponse = await fetch(`${aiServiceUrl}/process-document`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        file_path: filePath,
        document_title: documentTitle,
        document_id: documentId,
      }),
    }).catch(() => null);

    // 3. Fallback: If JSON path fails (e.g. cloud/remote container without shared disk), use multipart form upload
    if (!aiResponse || !aiResponse.ok) {
      if (fileBuffer && originalFilename) {
        const formData = new FormData();
        const uint8 = new Uint8Array(fileBuffer);
        const blob = new Blob([uint8]);
        formData.append("file", blob, originalFilename);
        formData.append("document_title", documentTitle);

        aiResponse = await fetch(`${aiServiceUrl}/upload-and-process`, {
          method: "POST",
          body: formData,
        }).catch(() => null);
      }
    }

    if (!aiResponse || !aiResponse.ok) {
      const errorText = aiResponse
        ? await aiResponse.text().catch(() => "")
        : `Layanan AI di ${aiServiceUrl} tidak dapat dijangkau. Pastikan FastAPI aktif di port 8000.`;
      throw new Error(errorText || "Gagal menghubungkan ke layanan AI.");
    }

    const result = await aiResponse.json();

    // 4. Update status to INDEXED with chunk and vector metrics
    await prisma.document.update({
      where: { id: documentId },
      data: {
        status: "INDEXED",
        chunksCount: result.total_chunks || 0,
        vectorCount: result.upserted_count || 0,
        errorMsg: null,
      },
    });
  } catch (error: any) {
    console.error(`[AI Pipeline Error] [${documentId}]:`, error);
    // 5. Update status to FAILED with readable explanation
    await prisma.document
      .update({
        where: { id: documentId },
        data: {
          status: "FAILED",
          errorMsg:
            error?.message ||
            `Gagal memproses AI. Pastikan server FastAPI di ${aiServiceUrl} aktif dan terhubung ke Pinecone.`,
        },
      })
      .catch(() => {});
  }
}
