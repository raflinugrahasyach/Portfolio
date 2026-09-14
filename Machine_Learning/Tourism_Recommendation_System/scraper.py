import os
import subprocess
import time
import pandas as pd
import glob
import random

# ==========================================
# KONFIGURASI DIREKTORI & ENGINE
# ==========================================
BASE_DIR = r"D:\STARTUP MAGANG PEKERJAAN\developer FREELANCE\14 Mei_Sistem Rekomendasi Wisata_200K"
ENGINE_PATH = os.path.join(BASE_DIR, "google_maps_scraper-1.12.1-windows-amd64.exe")
OUTPUT_DIR = os.path.join(BASE_DIR, "hasil_sementara")
TEMP_QUERY_FILE = os.path.join(BASE_DIR, "temp_query.txt")

# Buat folder penyimpanan sementara jika belum ada
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ==========================================
# DAFTAR KUERI PENCARIAN (TARGET 7000+ DATA)
# ==========================================
KATA_KUNCI = [
    "Tempat wisata di", 
    "Taman rekreasi di", 
    "Wisata alam di", 
    "Pantai di", 
    "Museum di"
]

KOTA_INDONESIA = [
    "Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar", "Palembang", 
    "Tangerang", "Depok", "Bekasi", "Batam", "Pekanbaru", "Bogor", "Padang", "Malang", 
    "Bali", "Denpasar", "Yogyakarta", "Balikpapan", "Banjarmasin", "Pontianak", "Cimahi", 
    "Surakarta", "Manado", "Mataram", "Kupang", "Jayapura", "Ambon", "Bengkulu", "Cirebon", 
    "Sukabumi", "Kediri", "Palu", "Tegal", "Purwokerto", "Tasikmalaya", "Banda Aceh", 
    "Tarakan", "Magelang", "Banyuwangi", "Jember", "Probolinggo", "Pasuruan", "Madiun", 
    "Salatiga", "Blitar", "Mojokerto", "Batu", "Pangkalpinang", "Ternate", "Bitung", 
    "Gorontalo", "Banjarbaru", "Singkawang", "Lhokseumawe", "Bontang", "Dumai", "Binjai"
]

# Membuat kombinasi Kueri (Contoh: "Tempat wisata di Surabaya")
semua_kueri = []
for kota in KOTA_INDONESIA:
    for keyword in KATA_KUNCI:
        semua_kueri.append(f"{keyword} {kota}")

# Acak urutan agar pencarian Google terlihat natural (seperti manusia)
random.shuffle(semua_kueri)

print(f"Total Kueri yang akan dijalankan: {len(semua_kueri)} kueri.")
print("Engine siap. Memulai proses scraping...\n")

# ==========================================
# ENGINE ORKESTRATOR (Eksekusi Low & Slow)
# ==========================================
for idx, kueri in enumerate(semua_kueri):
    # Nama file output untuk kueri ini
    safe_nama = kueri.replace(" ", "_").lower()
    output_csv = os.path.join(OUTPUT_DIR, f"res_{idx}_{safe_nama}.csv")
    
    # Lewati jika kueri ini sudah pernah di-scrape (Auto-Resume jika script mati)
    if os.path.exists(output_csv):
        print(f"[{idx+1}/{len(semua_kueri)}] Melewati '{kueri}' (Sudah ada di folder)")
        continue

    print(f"[{idx+1}/{len(semua_kueri)}] Scraping: '{kueri}'...")
    
    # Tulis kueri tunggal ke file txt sementara
    with open(TEMP_QUERY_FILE, "w", encoding="utf-8") as f:
        f.write(kueri)
        
    # Perintah memanggil .exe dengan argumen anti-banned
    # -c 1 : Concurrency 1 (Paling aman untuk IP rumah)
    # -depth 3 : Scroll ke bawah 3 kali (Mendapatkan ~60-100 tempat per kueri)
    # -extra-reviews : Wajib agar menarik detail ulasan (untuk kebutuhan SOW client)
    # -lang id : Output ulasan dalam bahasa Indonesia
    command = [
        ENGINE_PATH,
        "-input", TEMP_QUERY_FILE,
        "-results", output_csv,
        "-c", "1",
        "-depth", "3",
        "-extra-reviews",
        "-lang", "id",
        "-debug"
    ]
    
    try:
        # Jalankan Scraper
        subprocess.run(command, check=True)
        print(f"   => Berhasil disimpan ke {output_csv}")
    except subprocess.CalledProcessError as e:
        print(f"   => [ERROR] Gagal scraping '{kueri}'. Lanjut ke kueri berikutnya.")
    
    # DELAY ANTI-BANNED (20 - 35 detik)
    waktu_tunggu = random.randint(20, 35)
    print(f"   => Tidur selama {waktu_tunggu} detik agar tidak diblokir Google...\n")
    time.sleep(waktu_tunggu)

print("\n==========================================")
print("TAHAP SCRAPING SELESAI! Memulai Penggabungan Data...")
print("==========================================\n")

# ==========================================
# AUTO-MERGE & DATA CLEANING
# ==========================================
all_files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
df_list = []

for file in all_files:
    try:
        df_temp = pd.read_csv(file)
        df_list.append(df_temp)
    except:
        continue

if df_list:
    df_final = pd.concat(df_list, ignore_index=True)
    
    # Membersihkan Duplikat (Berdasarkan ID Tempat Google Maps)
    # Kolom standar gosom biasanya bernama 'place_id' atau 'title'
    if 'place_id' in df_final.columns:
        df_final = df_final.drop_duplicates(subset=['place_id'])
    elif 'title' in df_final.columns:
        df_final = df_final.drop_duplicates(subset=['title'])
        
    final_output_path = os.path.join(BASE_DIR, "FINAL_DATASET_7000.csv")
    df_final.to_csv(final_output_path, index=False)
    
    print(f"SUPER MANTAP! File final berhasil dibuat di:")
    print(final_output_path)
    print(f"Total Tempat Wisata Unik yang Didapat: {len(df_final)} baris data.")
    print("Dataset ini siap dihajar dengan algoritma NLP (SBERT) + Haversine Formula!")
else:
    print("Tidak ada file CSV yang ditemukan di folder hasil_sementara.")

# Hapus file query sementara
if os.path.exists(TEMP_QUERY_FILE):
    os.remove(TEMP_QUERY_FILE)