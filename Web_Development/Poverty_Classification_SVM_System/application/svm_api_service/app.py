import pandas as pd
import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Muat model dan scaler
try:
    model = joblib.load('model/svm_model.joblib')
    scaler = joblib.load('model/scaler.joblib')
    print("--- Model dan Scaler berhasil dimuat ---")
except Exception as e:
    model, scaler = None, None
    print(f"Error memuat model/scaler: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not scaler:
        return jsonify({'error': 'Model atau Scaler tidak termuat.'}), 500

    json_payload = request.get_json()
    if not json_payload or 'data' not in json_payload:
        return jsonify({'error': 'Request harus berisi JSON dengan key "data"'}), 400
    
    data_from_php = json_payload['data']

    try:
        # PERBAIKAN LOGIKA:
        # Urutan kolom ini HARUS SAMA PERSIS dengan saat model dilatih
        feature_order = [
            'Jenis Kelamin', 'Pendidikan', 'Pekerjaan', 'Status Perkawinan', 
            'Tanggungan Anak', 'Lantai Rumah', 'Dinding Rumah', 'Daya Listrik', 'Sumber Air'
        ]

        # Buat list berisi nilai-nilai dari PHP sesuai urutan di atas
        input_values = [
            data_from_php['jenis_kelamin'],
            data_from_php['pendidikan'],
            data_from_php['pekerjaan'],
            data_from_php['status_perkawinan'],
            data_from_php['tanggungan_anak'],
            data_from_php['lantai_rumah'],
            data_from_php['dinding_rumah'],
            data_from_php['daya_listrik'],
            data_from_php['sumber_air']
        ]
        
        # Buat DataFrame dari list nilai dengan nama kolom yang benar
        df_input = pd.DataFrame([input_values], columns=feature_order)

        # Langsung scaling dan prediksi karena data sudah numerik
        scaled_input = scaler.transform(df_input)
        prediction = model.predict(scaled_input)
        
        hasil_prediksi = 'Miskin' if prediction[0] == 1 else 'Tidak Miskin'
        
        return jsonify({'prediction': hasil_prediksi})

    except Exception as e:
        return jsonify({'error': f'Kesalahan internal saat prediksi: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
