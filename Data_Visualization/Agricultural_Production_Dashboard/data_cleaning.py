import pandas as pd
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

base_path = r"D:\STARTUP MAGANG PEKERJAAN\developer FREELANCE\29 Mei_Membuat analytics interface Tableau_200K"

df_list = []

def clean_lokasi(df):
    df['Lokasi'] = df['Lokasi'].astype(str).str.strip().str.upper()
    df = df[~df['Lokasi'].str.contains('JUMLAH|TOTAL', case=False, na=False)]
    return df

print("Memproses ATAP PADI DAN JAGUNG 2024.xlsx...")
# 1. ATAP PADI DAN JAGUNG 2024.xlsx
path_1 = os.path.join(base_path, "ATAP PADI DAN JAGUNG 2024.xlsx")
df1_raw = pd.read_excel(path_1, skiprows=4, header=None)
df1_raw.columns = ['No', 'Lokasi',
                   'Padi_Luas_Panen_Ha', 'Padi_Produksi_Ton', 'Padi_Produktivitas_Ku_Ha',
                   'Jagung_Luas_Panen_Ha', 'Jagung_Produksi_Ton', 'Jagung_Produktivitas_Ku_Ha',
                   'Kedelai_Luas_Panen_Ha', 'Kedelai_Produksi_Ton', 'Kedelai_Produktivitas_Ku_Ha']
df1 = df1_raw.dropna(subset=['Lokasi']).copy()
df1 = clean_lokasi(df1)
df1_melted = df1.drop('No', axis=1, errors='ignore').melt(id_vars=['Lokasi'], var_name='Komoditas_Metrik', value_name='Value')
df1_melted[['Komoditas', 'Metrik']] = df1_melted['Komoditas_Metrik'].str.split('_', n=1, expand=True)
df1_pivot = df1_melted.pivot_table(index=['Lokasi', 'Komoditas'], columns='Metrik', values='Value', aggfunc='first').reset_index()

df1_pivot['Tahun'] = 2024
df1_pivot['Periode'] = 'Tahunan'
df1_pivot['Tipe_Lokasi'] = 'Kabupaten/Kota' 
df_list.append(df1_pivot)

print("Memproses ATAP PADI 2025.xlsx...")
# 2. ATAP PADI 2025.xlsx
path_2 = os.path.join(base_path, "ATAP PADI 2025.xlsx")
df2_raw = pd.read_excel(path_2, header=None)
months = df2_raw.iloc[1].tolist()
metrics = df2_raw.iloc[0].ffill().tolist()
cols = []
for m, c in zip(metrics, months):
    if pd.isna(c):
        cols.append(m)
    else:
        cols.append(f"{m}_{c}")
df2_raw.columns = cols
df2 = df2_raw.iloc[2:].copy()
if 'Kabupaten' in df2.columns:
    df2.rename(columns={'Kabupaten': 'Lokasi'}, inplace=True)
df2 = df2.dropna(subset=['Lokasi'])
df2 = clean_lokasi(df2)

luas_cols = [c for c in df2.columns if 'Luas Panen' in str(c) and '25' in str(c) and 'Jan-Des' not in str(c)]
prod_cols = [c for c in df2.columns if 'Produksi Padi' in str(c) and '25' in str(c) and 'Jan-Des' not in str(c)]

df2_luas = df2[['Lokasi'] + luas_cols].melt(id_vars=['Lokasi'], var_name='Col', value_name='Luas_Panen_Ha')
df2_luas['Periode'] = df2_luas['Col'].apply(lambda x: x.split('_')[-1])

df2_prod = df2[['Lokasi'] + prod_cols].melt(id_vars=['Lokasi'], var_name='Col', value_name='Produksi_Ton')
df2_prod['Periode'] = df2_prod['Col'].apply(lambda x: x.split('_')[-1])

df2_merged = pd.merge(df2_luas[['Lokasi', 'Periode', 'Luas_Panen_Ha']], 
                      df2_prod[['Lokasi', 'Periode', 'Produksi_Ton']], 
                      on=['Lokasi', 'Periode'])
df2_merged['Produktivitas_Ku_Ha'] = 0.0
df2_merged['Tahun'] = 2025
df2_merged['Komoditas'] = 'Padi'
df2_merged['Tipe_Lokasi'] = 'Kabupaten/Kota'
df_list.append(df2_merged)

print("Memproses ATAP JAGUNG 2024.xlsx...")
# 3. ATAP JAGUNG 2024.xlsx
path_3 = os.path.join(base_path, "ATAP JAGUNG 2024.xlsx")
df3_raw = pd.read_excel(path_3, header=None)
caturwulans = df3_raw.iloc[2].ffill().tolist()
metrics = df3_raw.iloc[3].tolist()
cols = []
for c, m in zip(caturwulans, metrics):
    if pd.isna(m):
        cols.append(c)
    else:
        cols.append(f"{c}_{m}")
df3_raw.columns = cols
df3 = df3_raw.iloc[4:].copy() 
if 'Kabupaten/Kota' in df3.columns:
    df3.rename(columns={'Kabupaten/Kota': 'Lokasi'}, inplace=True)

df3 = df3.dropna(subset=['Lokasi'])
# Try to filter out metadata rows
df3 = df3[df3['Lokasi'].astype(str) != '-2']
df3 = clean_lokasi(df3)

periods = ['Jan-April', 'Mei-Agustus', 'Sep-Des']
df3_melted_list = []
for p in periods:
    temp = df3[['Lokasi', f"{p}_Luas Panen (Ha)", f"{p}_Produksi (Ton)", f"{p}_Hasil Per Hektar (Ku/Ha)"]].copy()
    temp.columns = ['Lokasi', 'Luas_Panen_Ha', 'Produksi_Ton', 'Produktivitas_Ku_Ha']
    temp['Periode'] = p
    df3_melted_list.append(temp)

df3_merged = pd.concat(df3_melted_list)
df3_merged['Tahun'] = 2024
df3_merged['Komoditas'] = 'Jagung'
df3_merged['Tipe_Lokasi'] = 'Kabupaten/Kota'
df_list.append(df3_merged)

print("Memproses Luas Panen, Produksi, dan Produktivitas Jagung Menurut Provinsi, 2024.xlsx...")
# 4. Luas Panen...
path_4 = os.path.join(base_path, "Luas Panen, Produksi, dan Produktivitas Jagung Menurut Provinsi, 2024.xlsx")
df4_raw = pd.read_excel(path_4, skiprows=4, header=None)
df4_raw.columns = ['Lokasi', 'Luas_Panen_Ha', 'Produktivitas_Ku_Ha', 'Produksi_Ton']
df4 = df4_raw.dropna(subset=['Lokasi']).copy()
df4 = clean_lokasi(df4)
df4['Tahun'] = 2024
df4['Periode'] = 'Tahunan'
df4['Komoditas'] = 'Jagung'
df4['Tipe_Lokasi'] = 'Provinsi'
df_list.append(df4)

print("Konsolidasi dan export...")
# 5. Konsolidasi
master_df = pd.concat(df_list, ignore_index=True)

for col in ['Luas_Panen_Ha', 'Produksi_Ton', 'Produktivitas_Ku_Ha']:
    # Replace non-numeric with NaN (like '-' or space)
    master_df[col] = pd.to_numeric(master_df[col], errors='coerce')

# Fill NaN with 0
master_df[['Luas_Panen_Ha', 'Produksi_Ton', 'Produktivitas_Ku_Ha']] = master_df[['Luas_Panen_Ha', 'Produksi_Ton', 'Produktivitas_Ku_Ha']].fillna(0)

# 1. Penyaringan Baris (Row Filtering)
exclude_substrings = ['KETERANGAN', 'LUAS PANEN', 'PRODUKSI', 'BERDASARKAN', 'MENCAPAI', '2025']
pattern = '|'.join(exclude_substrings)
master_df = master_df[~master_df['Lokasi'].str.contains(pattern, case=False, na=False)]

# 2. Pemetaan Penamaan (String Mapping)
location_mapping = {
    'KOTA PALEMBANG': 'PALEMBANG',
    'KOTA PRABUMULIH': 'PRABUMULIH',
    'KOTA PAGAR ALAM': 'PAGAR ALAM',
    'KOTA LUBUKLINGGAU': 'LUBUKLINGGAU',
    'OKU SELATAN': 'OGAN KOMERING ULU SELATAN',
    'OKU TIMUR': 'OGAN KOMERING ULU TIMUR',
    'BANYU ASIN': 'BANYUASIN'
}
master_df['Lokasi'] = master_df['Lokasi'].replace(location_mapping)

# 3. Klasifikasi Level Entitas
master_df.loc[master_df['Lokasi'] == 'INDONESIA', 'Tipe_Lokasi'] = 'Nasional'

# Reorder columns
target_cols = ['Lokasi', 'Tipe_Lokasi', 'Komoditas', 'Tahun', 'Periode', 'Luas_Panen_Ha', 'Produksi_Ton', 'Produktivitas_Ku_Ha']
master_df = master_df[target_cols]

out_path = os.path.join(base_path, "Database_Panen_Clean.xlsx")
master_df.to_excel(out_path, index=False)

print("\n--- Verifikasi Data Akhir ---")
print(master_df.head(10))
print("\n")
master_df.info()
print(f"\nBerhasil mengekspor dataset gabungan ke: {out_path}")
