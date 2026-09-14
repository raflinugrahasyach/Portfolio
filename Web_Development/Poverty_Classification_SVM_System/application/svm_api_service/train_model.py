# train_svm.py
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

print("--- Memulai Proses Pelatihan Model SVM (Struktur CSV Baru) ---")

# 1. Muat Dataset
csv_file = 'dummy_penduduk_desa_taraju.csv'
if not os.path.exists(csv_file):
    raise FileNotFoundError(f"File '{csv_file}' tidak ditemukan.")

df = pd.read_csv(csv_file)
print(f"Dataset '{csv_file}' berhasil dimuat. Ukuran: {df.shape}")

# 2. Pilih kolom fitur dan target
feature_cols = [
    'Jenis Kelamin', 'Pendidikan', 'Pekerjaan', 'Status Perkawinan',
    'Tanggungan Anak', 'Lantai Rumah', 'Dinding Rumah', 'Daya Listrik', 'Sumber Air'
]
target_col = 'Kelas'

X = df[feature_cols].copy()
y = df[target_col].copy()

# 3. Encoding fitur teks ke numerik dengan LabelEncoder
encoders = {}
for col in feature_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le
print("Proses encoding fitur teks ke numerik selesai.")

# 4. Encoding target kelas
le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)
print(f"Label kelas: {list(le_target.classes_)}")

# 5. Pisahkan Data Latih dan Uji
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# 6. Scaling fitur
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("Scaling fitur untuk data latih dan uji berhasil dilakukan.")

# 7. Latih Model SVM
model = SVC(kernel='linear', class_weight='balanced', random_state=42)
model.fit(X_train_scaled, y_train)
print("Model SVM berhasil dilatih.")

# 8. Evaluasi Model
y_pred = model.predict(X_test_scaled)
print("\n--- Hasil Evaluasi Model pada Data Uji ---")
print(f"Akurasi: {accuracy_score(y_test, y_pred):.4f}")
print("\nLaporan Klasifikasi:")
print(classification_report(y_test, y_pred, labels=range(len(le_target.classes_)), target_names=[str(x) for x in le_target.classes_], zero_division=0))

# 9. Simpan Model, Scaler, dan Encoder
output_dir = 'model'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

joblib.dump(model, os.path.join(output_dir, 'svm_model.joblib'))
joblib.dump(scaler, os.path.join(output_dir, 'scaler.joblib'))
joblib.dump(encoders, os.path.join(output_dir, 'feature_encoders.joblib'))
joblib.dump(le_target, os.path.join(output_dir, 'target_encoder.joblib'))

print(f"Model dan artefak encoding berhasil disimpan di folder '{output_dir}'.")
print("--- PROSES PELATIHAN SELESAI DENGAN SUKSES ---")
