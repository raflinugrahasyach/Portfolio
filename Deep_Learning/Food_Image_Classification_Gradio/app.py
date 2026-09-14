import gradio as gr
import tensorflow as tf
import numpy as np

# Kelas target berdasarkan direktori dataset
CLASS_NAMES = [
    'Burger', 'Gado-Gado', 'Pizza', 'Rawon', 'Rendang', 
    'Sate', 'Soto', 'Ayam Goreng', 'French Fries', 
    'Ikan Goreng', 'Mie Goreng', 'Nasi Goreng', 'Nasi Padang'
]

# Muat model Keras
try:
    model = tf.keras.models.load_model('model_weights.h5')
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

def predict(image):
    if model is None:
        return {"Error: Model 'model_weights.h5' tidak ditemukan": 1.0}
    
    # Preprocessing citra sesuai dengan arsitektur model
    img = image.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0  # Normalisasi
    img_array = tf.expand_dims(img_array, 0)
    
    # Inferensi
    predictions = model.predict(img_array)
    
    # Softmax jika lapisan terakhir belum menggunakan aktivasi softmax
    score = tf.nn.softmax(predictions[0]) if np.max(predictions[0]) > 1.0 else predictions[0]
    
    confidences = {CLASS_NAMES[i]: float(score[i]) for i in range(len(CLASS_NAMES))}
    return confidences

iface = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil", label="Unggah Citra Makanan"),
    outputs=gr.Label(num_top_classes=3, label="Hasil Klasifikasi"),
    title="🍔 Pengklasifikasi Makanan (Gradio)",
    description="Sistem pengenalan gambar makanan berbasis Convolutional Neural Network (CNN) kustom. Dapat membedakan 13 jenis masakan populer lokal maupun internasional.",
    allow_flagging="never"
)

if __name__ == '__main__':
    iface.launch()
