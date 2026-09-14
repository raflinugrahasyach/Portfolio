import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import warnings

# Mengabaikan peringatan konvergensi dari statsmodels agar tidak muncul di aplikasi
warnings.filterwarnings("ignore")

# Konfigurasi halaman dasar
st.set_page_config(page_title="Sistem Peramalan Keraton Kasepuhan", layout="wide")

st.title("Sistem Peramalan Data Keraton Kasepuhan Cirebon")
st.write("Aplikasi untuk memprediksi data operasional berdasarkan data historis tiket.")

# ==========================================
# TAHAP 1: UNGGAH DATA
# ==========================================
st.header("1. Unggah Data Historis")
uploaded_file = st.file_uploader("Pilih berkas Excel (.xlsx)", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Membaca sheet utama berdasarkan struktur data stakeholder
        df = pd.read_excel(uploaded_file, sheet_name='Pendapatan Tiket Tahun 2024')
        
        st.write("Pratinjau Data Mentah:")
        st.dataframe(df.head())

        # ==========================================
        # TAHAP 2: PEMBERSIHAN DATA
        # ==========================================
        st.header("2. Pembersihan Data")
        
        # Menghapus baris yang kosong pada kolom esensial (Tanggal dan Jumlah)
        df.dropna(subset=['Tanggal', 'Jumlah'], inplace=True)
        
        # Konversi format Tanggal menjadi objek datetime
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        
        # Memastikan kolom Jumlah bernilai numerik
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        
        # Menghapus baris dengan data tanggal atau nominal yang tidak valid pasca-konversi
        df.dropna(subset=['Tanggal', 'Jumlah'], inplace=True)

        st.write("Pratinjau Data Bersih:")
        st.dataframe(df.head())
        
        st.success("Data berhasil diunggah dan dibersihkan. Sistem siap untuk tahap visualisasi dan peramalan.")

        # ==========================================
        # TAHAP 3: VISUALISASI DATA MINGGUAN
        # ==========================================
        st.header("3. Visualisasi Tren Kunjungan Mingguan")
        
        # Mengurutkan data berdasarkan tanggal dari yang paling lama
        df = df.sort_values('Tanggal')
        
        # Mengatur kolom 'Tanggal' sebagai index untuk proses agregasi waktu
        df_time = df.set_index('Tanggal')
        
        # Agregasi (resample) data secara mingguan ('W') dan menghitung jumlah kunjungan
        df_weekly = df_time['Jumlah'].resample('W').sum().reset_index()
        df_weekly.columns = ['Minggu', 'Jumlah Kunjungan Aktual']
        
        st.write("Tabel Rekapitulasi Kunjungan Mingguan:")
        st.dataframe(df_weekly)
        
        st.subheader("Grafik Kunjungan Aktual Mingguan")
        st.line_chart(df_weekly.set_index('Minggu')['Jumlah Kunjungan Aktual'])

        # ==========================================
        # TAHAP 4: PERAMALAN NAIVE METHOD
        # ==========================================
        st.header("4. Peramalan (Naive Method)")
        st.write("Naive Method memprediksi bahwa nilai pada periode berikutnya akan sama dengan nilai pada periode saat ini.")
        
        df_weekly['Prediksi Naive'] = df_weekly['Jumlah Kunjungan Aktual'].shift(1)
        
        st.subheader("Grafik Perbandingan: Aktual vs Prediksi Naive")
        chart_data_naive = df_weekly.set_index('Minggu')[['Jumlah Kunjungan Aktual', 'Prediksi Naive']]
        st.line_chart(chart_data_naive)
        
        # ==========================================
        # TAHAP 5: PERAMALAN MOVING AVERAGE
        # ==========================================
        st.header("5. Peramalan (Moving Average)")
        st.write("Moving Average menghitung rata-rata dari 3 periode sebelumnya.")
        
        df_weekly['Prediksi Moving Average'] = df_weekly['Jumlah Kunjungan Aktual'].rolling(window=3).mean().shift(1)
        
        st.subheader("Grafik Perbandingan: Aktual vs Prediksi Moving Average")
        chart_data_ma = df_weekly.set_index('Minggu')[['Jumlah Kunjungan Aktual', 'Prediksi Moving Average']]
        st.line_chart(chart_data_ma)

        # ==========================================
        # TAHAP 6: PERAMALAN ARIMA
        # ==========================================
        st.header("6. Peramalan (ARIMA)")
        st.write("ARIMA memodelkan data berdasarkan hubungan nilai masa lalu (AR), proses differencing (I), dan nilai eror masa lalu (MA).")
        
        try:
            # Menggunakan parameter order (1,1,1) sebagai standar awal yang cukup ringan
            model_arima = ARIMA(df_weekly['Jumlah Kunjungan Aktual'], order=(1, 1, 1))
            hasil_arima = model_arima.fit()
            
            # Mendapatkan nilai prediksi historis (in-sample)
            df_weekly['Prediksi ARIMA'] = hasil_arima.fittedvalues
            # Baris pertama dikosongkan karena proses differencing
            df_weekly.loc[0, 'Prediksi ARIMA'] = np.nan
            
            st.subheader("Grafik Perbandingan: Aktual vs Prediksi ARIMA")
            chart_data_arima = df_weekly.set_index('Minggu')[['Jumlah Kunjungan Aktual', 'Prediksi ARIMA']]
            st.line_chart(chart_data_arima)
            
            st.success("Model ARIMA berhasil diterapkan pada data historis.")
            
        except Exception as e:
            st.warning(f"Data tidak cukup stabil untuk diproses oleh model ARIMA. Pesan sistem: {e}")
            df_weekly['Prediksi ARIMA'] = np.nan

        # ==========================================
        # TAHAP 7: EVALUASI EROR KESELURUHAN
        # ==========================================
        st.header("7. Evaluasi Akurasi Peramalan")
        
        def hitung_mae(aktual, prediksi):
            aktual, prediksi = np.array(aktual), np.array(prediksi)
            mask = ~np.isnan(aktual) & ~np.isnan(prediksi)
            return np.mean(np.abs(aktual[mask] - prediksi[mask]))

        def hitung_mape(aktual, prediksi):
            aktual, prediksi = np.array(aktual), np.array(prediksi)
            mask = ~np.isnan(aktual) & ~np.isnan(prediksi) & (aktual != 0)
            return np.mean(np.abs((aktual[mask] - prediksi[mask]) / aktual[mask])) * 100

        # Naive
        mae_naive = hitung_mae(df_weekly['Jumlah Kunjungan Aktual'], df_weekly['Prediksi Naive'])
        mape_naive = hitung_mape(df_weekly['Jumlah Kunjungan Aktual'], df_weekly['Prediksi Naive'])

        # MA
        mae_ma = hitung_mae(df_weekly['Jumlah Kunjungan Aktual'], df_weekly['Prediksi Moving Average'])
        mape_ma = hitung_mape(df_weekly['Jumlah Kunjungan Aktual'], df_weekly['Prediksi Moving Average'])

        # ARIMA
        mae_arima = hitung_mae(df_weekly['Jumlah Kunjungan Aktual'], df_weekly['Prediksi ARIMA'])
        mape_arima = hitung_mape(df_weekly['Jumlah Kunjungan Aktual'], df_weekly['Prediksi ARIMA'])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Naive Method")
            st.write(f"**MAE:** {mae_naive:,.2f}")
            st.write(f"**MAPE:** {mape_naive:.2f}%")
        with col2:
            st.subheader("Moving Average")
            st.write(f"**MAE:** {mae_ma:,.2f}")
            st.write(f"**MAPE:** {mape_ma:.2f}%")
        with col3:
            st.subheader("ARIMA")
            st.write(f"**MAE:** {mae_arima:,.2f}")
            st.write(f"**MAPE:** {mape_arima:.2f}%")

        # ==========================================
        # TAHAP 8: DECISION RULE KESELURUHAN
        # ==========================================
        st.header("8. Rekomendasi Keputusan (Decision Rule)")
        
        kunjungan_minggu_terakhir = df_weekly['Jumlah Kunjungan Aktual'].iloc[-1]
        
        # Prediksi masa depan
        prediksi_depan_ma = df_weekly['Jumlah Kunjungan Aktual'].tail(3).mean()
        
        st.write(f"Kunjungan minggu terakhir: **{kunjungan_minggu_terakhir:,.0f} Orang**")
        st.write(f"Prediksi minggu depan (Moving Average): **{prediksi_depan_ma:,.0f} Orang**")
        
        try:
            prediksi_depan_arima = hasil_arima.forecast(steps=1).iloc[0]
            st.write(f"Prediksi minggu depan (ARIMA): **{prediksi_depan_arima:,.0f} Orang**")
        except:
            pass
        
        if prediksi_depan_ma > kunjungan_minggu_terakhir:
            st.success("Rekomendasi (berdasarkan MA): Tren kunjungan diprediksi naik. Pertahankan strategi saat ini dan pastikan kesiapan staf layanan operasional mencukupi.")
        elif prediksi_depan_ma < kunjungan_minggu_terakhir:
            st.warning("Rekomendasi (berdasarkan MA): Tren kunjungan diprediksi menurun. Disarankan untuk meningkatkan promosi di media sosial atau merencanakan program khusus daya tarik wisata.")
        else:
            st.info("Rekomendasi (berdasarkan MA): Tren kunjungan diprediksi stabil. Lakukan evaluasi operasional rutin.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses berkas: {e}")
else:
    st.info("Silakan unggah berkas data Excel untuk memulai sistem.")