# 🍎 Real-Time Industrial Fruit Sorting & Ripeness Inspection (MobileNetV2 + Flask)

## 📖 Overview & Industrial Value
Post-harvest agricultural processing relies heavily on rapid, automated quality control (QC) to minimize post-harvest losses, standardize packaging grades, and optimize supply-chain throughput. Traditional rule-based color thresholding in computer vision frequently degrades under fluctuating ambient factory illumination, sensor noise, and natural surface blemishes.

This project delivers an end-to-end deep learning visual sorting prototype engineered for high-speed conveyor pipelines. By combining a lightweight **MobileNetV2** backbone with a **Flask** and **OpenCV** streaming server, the system differentiates apples from tomatoes while concurrently performing fine-grained maturity inspection on tomatoes (ripe vs. unripe) in real time.

---

## 🍅 Dataset & Augmentation Pipeline
The model was trained on a balanced corpus of approximately **3,600 standardized images** (~1,200 instances per class) curated across three operational categories:

- **`apel` (Apples)**: Red dessert apples exhibiting diverse specular reflections.
- **`tomat_masak` (Ripe Tomatoes)**: Fully mature, deep-red tomatoes ready for commercial distribution.
- **`tomat_mentah` (Unripe Tomatoes)**: Immature, green-to-yellowish tomatoes requiring maturation buffering.

### Environmental Simulation Pipeline:
To ensure resilience against fluctuating factory lighting and mechanical vibration on sorting belts, the data generator implements heavy real-time augmentations:
- **Dynamic Photometric Jitter**: `brightness_range=[0.6, 1.4]` to withstand lumen variance between daylight and industrial fluorescent fixtures.
- **Geometric Transformations**: Random rotations ($\pm 25^\circ$), affine shear ($0.2$), and dimensional shifts ($0.2$ width/height).
- **Target Rescaling**: Bilinear interpolation resizing to $224 \times 224 \times 3$ normalized tensors.

---

## 🧠 Model Architecture & Edge Optimization
Given the operational requirement for high-throughput edge inference (30+ FPS on consumer-grade hardware), **MobileNetV2** was selected as the optimal feature extractor:

1. **Inverted Residual & Linear Bottleneck Backbone**:
   - Depthwise separable convolutions significantly reduce parameter count and multiply-accumulate (MAC) operations compared to standard 2D convolutions.
   - Pre-trained ImageNet weights retained with frozen feature layers (`trainable = False`) to prevent catastrophic forgetting.
2. **Specialized Classification Head**:
   - `GlobalAveragePooling2D()` layer collapsing spatial dimensions into a compact 1,280-dimensional embedding.
   - Fully connected projection layer `Dense(128, activation='relu')` with dropout regularization.
   - Output layer `Dense(3, activation='softmax')` providing calibrated class probability distributions.
3. **Training & Serialization**:
   - Optimized via **Adam** with categorical cross-entropy loss over 15 epochs, achieving rapid, stable convergence.
   - Exported production artifact saved as `model_buah_v1.h5`.

---

## 📊 Key Results & Inference Metrics
- **Validation Accuracy**: `>96.5%` across test batches.
- **Inference Latency**: `<25 ms` per frame on CPU, comfortably exceeding real-time video streaming thresholds (30 FPS).
- **Sorting Sensitivity**: High class separation boundary between red apples and red ripe tomatoes, overcoming superficial chromatic similarities via learned structural fruit geometry.

---

## 🚀 How to Run the Real-Time Web Prototype

The application couples a multi-threaded OpenCV video capture pipeline with a Flask web dashboard.

### 1. Navigate to Web Application Root
```bash
cd Project_Sortir_Buah
```

### 2. Install Required Dependencies
```bash
pip install flask opencv-python tensorflow numpy pillow
```

### 3. Start the Flask Inference Server
```bash
python app.py
```

### 4. Access the Live Dashboard
Open `http://localhost:5000/dashboard` in any web browser. The system initializes the primary video capture device (Camera Index 0), streaming live annotated bounding boxes and classification confidences.

---

## 🖼️ Interface Preview
![Project Preview](./preview.png)
