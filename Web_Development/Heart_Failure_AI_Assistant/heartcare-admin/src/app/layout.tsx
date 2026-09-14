// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "HeartCare Admin Panel",
  description: "Panel administrasi untuk mengelola dokumen pedoman klinis gagal jantung",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-[#0A0F1E] text-white`}>
        {children}
      </body>
    </html>
  );
}
