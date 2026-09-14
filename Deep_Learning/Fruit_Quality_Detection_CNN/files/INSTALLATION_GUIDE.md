# Fruit Quality Detection CNN - Installation Guide

`	ext
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     🍎 IoT FRUIT SORTING SYSTEM - PIXEL-PERFECT EDITION          ║
║                  PANDUAN INSTALASI LENGKAP                        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

📋 DAFTAR ISI:
─────────────────────────────────────────────────────────────────────

1. Requirements & Prerequisites
2. Cara Install Python (Windows/Mac/Linux)
3. Install Dependencies
4. Menjalankan Aplikasi
5. Troubleshooting
6. Tips & Tricks

═══════════════════════════════════════════════════════════════════════
1️⃣  REQUIREMENTS & PREREQUISITES
═══════════════════════════════════════════════════════════════════════

✅ Yang Anda Butuhkan:

• Python 3.8 atau lebih tinggi
• pip (package manager Python)
• Webcam/kamera (untuk fitur deteksi)
• Browser modern (Chrome/Firefox recommended)
• Koneksi internet (untuk install library)
• Text editor (VS Code, Sublime, Notepad++ - optional)

💻 Minimum System Requirements:

• OS: Windows 7+, macOS 10.12+, atau Linux
• RAM: 2GB (4GB recommended)
• Storage: 100MB free space
• Processor: Intel Core i3 atau equivalent

═══════════════════════════════════════════════════════════════════════
2️⃣  CARA INSTALL PYTHON
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ 🪟 WINDOWS                                                          │
└─────────────────────────────────────────────────────────────────────┘

Langkah 1: Download Python
   • Buka: https://www.python.org/downloads/
   • Klik "Download Python 3.11" (atau versi terbaru)
   • File akan terdownload (sekitar 25MB)

Langkah 2: Install Python
   • Double-click file installer yang terdownload
   • ⚠️ PENTING: Centang "Add Python to PATH"
   • Klik "Install Now"
   • Tunggu proses instalasi selesai
   • Klik "Close"

Langkah 3: Verifikasi Instalasi
   • Buka Command Prompt (tekan Win+R, ketik "cmd", Enter)
   • Ketik: python --version
   • Seharusnya muncul: Python 3.11.x
   • Ketik: pip --version
   • Seharusnya muncul: pip 23.x.x

Jika command tidak ditemukan:
   • Restart komputer
   • Atau install ulang dengan centang "Add to PATH"

┌─────────────────────────────────────────────────────────────────────┐
│ 🍎 macOS                                                            │
└─────────────────────────────────────────────────────────────────────┘

Metode 1: Homebrew (Recommended)
   • Buka Terminal (Applications → Utilities → Terminal)
   • Install Homebrew:
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   • Install Python:
     brew install python@3.11
   • Verifikasi:
     python3 --version
     pip3 --version

Metode 2: Download Langsung
   • Download dari: https://www.python.org/downloads/mac-osx/
   • Buka file .pkg yang terdownload
   • Ikuti wizard instalasi
   • Verifikasi di Terminal

┌─────────────────────────────────────────────────────────────────────┐
│ 🐧 LINUX (Ubuntu/Debian)                                           │
└─────────────────────────────────────────────────────────────────────┘

   • Buka Terminal (Ctrl+Alt+T)
   • Update package list:
     sudo apt update
   • Install Python:
     sudo apt install python3 python3-pip
   • Verifikasi:
     python3 --version
     pip3 --version

═══════════════════════════════════════════════════════════════════════
3️⃣  INSTALL DEPENDENCIES
═══════════════════════════════════════════════════════════════════════

Langkah 1: Buka Terminal/Command Prompt
   • Windows: Win+R → ketik "cmd" → Enter
   • Mac: Cmd+Space → ketik "terminal" → Enter
   • Linux: Ctrl+Alt+T

Langkah 2: Navigasi ke Folder Project
   • Windows:
     cd C:\Users\YourName\Desktop\iot-fruit-sorting

   • Mac/Linux:
     cd ~/Desktop/iot-fruit-sorting

   💡 Tips: Drag & drop folder ke terminal untuk auto-fill path

Langkah 3: Install Flask

   Opsi A: Install Flask saja (paling sederhana)
   ────────────────────────────────────────────
   pip install Flask

   Atau jika menggunakan Python 3 di Linux/Mac:
   pip3 install Flask

   Opsi B: Install dari requirements.txt
   ──────────────────────────────────────
   pip install -r requirements.txt

Langkah 4: Verifikasi Instalasi
   • Ketik: pip list
   • Cari "Flask" dalam list
   • Seharusnya muncul: Flask 3.0.0 (atau versi terbaru)

Troubleshooting Install:
────────────────────────

❌ "pip is not recognized"
   → Python tidak di PATH
   → Solusi: Install ulang Python dengan centang "Add to PATH"

❌ "Permission denied" atau "Access denied"
   → Gunakan sudo (Linux/Mac): sudo pip3 install Flask
   → Atau jalankan CMD as Administrator (Windows)

❌ "Could not find a version that satisfies"
   → Internet connection issue
   → Solusi: Cek koneksi internet, retry install

❌ "ERROR: Failed building wheel"
   → Update pip: pip install --upgrade pip
   → Retry install

═══════════════════════════════════════════════════════════════════════
4️⃣  MENJALANKAN APLIKASI
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ METODE 1: Jalankan dari Terminal (RECOMMENDED)                     │
└─────────────────────────────────────────────────────────────────────┘

Langkah 1: Buka Terminal di Folder Project

Langkah 2: Jalankan Aplikasi
   
   Windows:
   ────────
   python app_new.py

   Mac/Linux:
   ──────────
   python3 app_new.py

Langkah 3: Lihat Output
   ════════════════════════════════════════════════════════════════
    🍎 IoT FRUIT SORTING SYSTEM - PIXEL-PERFECT EDITION
   ════════════════════════════════════════════════════════════════
   
   ✅ Server berhasil dijalankan!
   
   📱 Buka browser dan akses:
      → http://localhost:5000
      → http://127.0.0.1:5000
   
   🔗 Halaman yang tersedia:
      • Dashboard     : http://localhost:5000/dashboard
      • Monitoring    : http://localhost:5000/monitoring
      • Pengenalan    : http://localhost:5000/pengenalan
      • Penyortiran   : http://localhost:5000/penyortiran
   ════════════════════════════════════════════════════════════════

Langkah 4: Buka Browser
   • Buka Chrome atau Firefox
   • Ketik di address bar: localhost:5000
   • Tekan Enter
   • Aplikasi akan terbuka! 🎉

Langkah 5: Menghentikan Server
   • Kembali ke Terminal
   • Tekan: Ctrl+C (Windows/Linux) atau Cmd+C (Mac)
   • Server akan berhenti

┌─────────────────────────────────────────────────────────────────────┐
│ METODE 2: Double-Click (Windows Only)                              │
└─────────────────────────────────────────────────────────────────────┘

   • Double-click file "app_new.py"
   • Pilih "Open with Python"
   • Terminal akan terbuka otomatis
   • Buka browser → localhost:5000

   ⚠️ Note: Metode ini tidak selalu work di semua sistem

═══════════════════════════════════════════════════════════════════════
5️⃣  TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ Problem: Port 5000 sudah digunakan                                 │
└─────────────────────────────────────────────────────────────────────┘

Error Message:
   "OSError: [Errno 48] Address already in use"

Solusi A: Matikan aplikasi yang menggunakan port 5000
────────────────────────────────────────────────────────

Windows:
   1. Cari process: netstat -ano | findstr :5000
   2. Catat PID (angka di kolom terakhir)
   3. Kill process: taskkill /PID <PID> /F

Mac/Linux:
   1. Cari process: lsof -ti:5000
   2. Kill process: kill -9 $(lsof -ti:5000)

Solusi B: Ubah port di app_new.py
──────────────────────────────────

   1. Buka app_new.py dengan text editor
   2. Cari baris: app.run(host='0.0.0.0', port=5000)
   3. Ubah 5000 menjadi 8080 atau port lain
   4. Save file
   5. Jalankan ulang aplikasi
   6. Akses: localhost:8080

┌─────────────────────────────────────────────────────────────────────┐
│ Problem: Kamera tidak bisa diakses                                 │
└─────────────────────────────────────────────────────────────────────┘

Solusi:
   1. Check browser permissions:
      • Chrome: Settings → Privacy → Site Settings → Camera
      • Firefox: Preferences → Privacy → Permissions → Camera
      • Allow access untuk localhost

   2. Tutup aplikasi lain yang menggunakan kamera:
      • Zoom, Skype, Teams, etc.

   3. Coba browser lain (Chrome recommended)

   4. Pastikan menggunakan HTTPS atau localhost
      (Camera API hanya work di secure context)

┌─────────────────────────────────────────────────────────────────────┐
│ Problem: Halaman tidak load / error 404                            │
└─────────────────────────────────────────────────────────────────────┘

Checklist:
   ☐ Pastikan server running (check terminal)
   ☐ URL benar: localhost:5000 (bukan localhost:500)
   ☐ Tidak ada typo di URL
   ☐ Clear browser cache (Ctrl+Shift+Delete)
   ☐ Try incognito mode

┌─────────────────────────────────────────────────────────────────────┐
│ Problem: Chart tidak muncul                                        │
└─────────────────────────────────────────────────────────────────────┘

Kemungkinan Penyebab:
   1. Internet connection issue (Chart.js dari CDN)
   2. Browser cache
   3. JavaScript error

Solusi:
   1. Cek koneksi internet
   2. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R di Mac)
   3. Buka Console (F12) → check error messages
   4. Clear browser cache

┌─────────────────────────────────────────────────────────────────────┐
│ Problem: Sample data tidak muncul                                  │
└─────────────────────────────────────────────────────────────────────┘

Solusi:
   1. Restart aplikasi (Ctrl+C, lalu python app_new.py lagi)
   2. Check terminal untuk error messages
   3. Coba reset data (klik tombol Reset Data di halaman)

═══════════════════════════════════════════════════════════════════════
6️⃣  TIPS & TRICKS
═══════════════════════════════════════════════════════════════════════

💡 Development Tips:
────────────────────

• Auto-reload saat edit code:
  Flask sudah include auto-reload di debug mode
  Edit file → Save → Refresh browser

• Lihat error messages:
  Selalu check terminal untuk error details

• Debug mode:
  Sudah enabled by default
  Jika mau disable: ubah debug=False di app.run()

🚀 Performance Tips:
────────────────────

• Clear browser cache regularly
• Close unused browser tabs
• Jangan buka terlalu banyak aplikasi bersamaan
• Monitor RAM usage (Task Manager / Activity Monitor)

🔒 Security Tips:
─────────────────

• Jangan expose ke public internet tanpa security
• Gunakan strong SECRET_KEY di production
• Enable HTTPS untuk production
• Implement user authentication jika perlu

📱 Browser Recommendations:
───────────────────────────

1. Google Chrome (Best)
   • Fastest performance
   • Best WebRTC support
   • Good developer tools

2. Mozilla Firefox (Good)
   • Good privacy
   • Stable performance
   • Decent WebRTC

3. Microsoft Edge (OK)
   • Chromium-based
   • Good compatibility

❌ AVOID:
   • Internet Explorer (not supported)
   • Old browser versions

⌨️  Keyboard Shortcuts:
───────────────────────

Halaman Pengenalan:
   • Space/Enter → Capture image (saat kamera aktif)
   • Escape → Stop camera

Browser:
   • F12 → Open developer tools
   • Ctrl+Shift+R → Hard refresh
   • Ctrl+Shift+Delete → Clear cache

═══════════════════════════════════════════════════════════════════════
📞 NEED HELP?
═══════════════════════════════════════════════════════════════════════

Jika masih mengalami masalah:

1. Baca ulang troubleshooting section
2. Check terminal/console untuk error messages
3. Google error message spesifik
4. Stack Overflow untuk masalah Flask
5. Contact tim development

═══════════════════════════════════════════════════════════════════════

🎉 SELAMAT! Anda berhasil setup IoT Fruit Sorting System!

Next Steps:
   ✓ Explore semua halaman
   ✓ Test fitur kamera
   ✓ Try detection simulation
   ✓ Customize sesuai kebutuhan

Happy Coding! 🚀

═══════════════════════════════════════════════════════════════════════
Last Updated: February 2026
Version: 2.0 Pixel-Perfect Edition
═══════════════════════════════════════════════════════════════════════

`
