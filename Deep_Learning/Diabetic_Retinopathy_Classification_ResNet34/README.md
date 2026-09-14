# 👁️ Diabetic Retinopathy Severity Grading with ResNet34

## 📖 Overview & Clinical Value
Diabetic Retinopathy (DR) is a chronic microvascular complication of diabetes and remains a leading cause of preventable visual impairment and acquired blindness among working-age adults globally. Conventional clinical diagnosis relies on specialized ophthalmological examinations and manual color fundus photography interpretation—a workflow constrained by specialist availability and inter-observer diagnostic variability.

This research project explores the efficacy of deep residual networks (**ResNet34**) combined with progressive fine-tuning techniques to automate early-stage detection and multi-class severity grading from digital fundus photography. The primary objective is to deliver an automated, computer-aided triage system capable of accurately ruling out healthy retinas with minimal false-negative risk while localizing subtle vascular lesions.

---

## 🔬 Dataset & Preprocessing Pipeline
The model was trained and evaluated on standardized 224×224-pixel retinal fundus images from the **Diabetic Retinopathy High-Resolution Dataset**, categorized into five standardized clinical stages:

- **Class 0 — `No_DR`**: Healthy retina showing clear macula, intact optic disc, and normal vascular tree.
- **Class 1 — `Mild`**: Presence of isolated microaneurysms without macular involvement.
- **Class 2 — `Moderate`**: Multiple microaneurysms, dot-and-blot hemorrhages, and venous beading.
- **Class 3 — `Severe`**: Over 20 intraretinal hemorrhages per quadrant, distinct venous beading in 2+ quadrants, or prominent IRMA.
- **Class 4 — `Proliferative_DR`**: Advanced stage with active neovascularization, vitreous preretinal hemorrhages, and fibrovascular proliferation.

### Preprocessing & Data Augmentation:
- **Spatial Transformations**: Random rotations (±30°), horizontal/vertical flipping, and zoom (0.9–1.1x) to simulate anatomical eye positioning and capture angle variance.
- **Color Jitter & Lighting**: Dynamic brightness and contrast adjustment to counteract uneven illumination across fundus camera lenses.
- **Tensor Normalization**: Normalized using ImageNet statistics ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$).

---

## 🧠 Model Architecture & Training Workflow
The architecture leverages a **ResNet34** backbone, implemented with **PyTorch** and **FastAI**:

1. **Feature Extractor**: Residual blocks with identity skip connections that mitigate vanishing gradients, enabling effective feature representation of both macro-structures (optic cup, arcade vessels) and micro-lesions (hard exudates, microaneurysms).
2. **Transfer Learning Stage**: The pre-trained convolutional base remained frozen while a custom adaptive pooling classification head (Adaptive Average + Max Pooling with BatchNorm and Dropout 0.5) was initialized and trained with cross-entropy loss.
3. **Discriminative Fine-Tuning**: Fully unfrozen residual stages trained with cyclic learning rates (`slice(1e-6, 1e-4)`), applying lower rates to earlier generic edge-detection layers and higher rates to deeper disease-specific feature maps.
4. **Model Artifact**: Serialized optimized model exported as `resnet34_fine_tune.pkl` for low-latency inference.

---

## 📊 Key Results & Performance Metrics
The fine-tuned model demonstrated robust discriminative power across unseen evaluation samples:

| Evaluation Metric | Score | Clinical Interpretation |
|-------------------|-------|-------------------------|
| **Global Accuracy** | **80.62%** | Overall correct multi-class stage predictions |
| **Macro Precision** | **65.57%** | Average precision across all five disease stages |
| **Macro Recall** | **61.65%** | Average sensitivity across clinical severity tiers |
| **Macro F1-Score** | **62.53%** | Balanced harmonic mean considering class distribution |
| **Healthy (`No_DR`) Precision** | **98.0%** | Exceptional specificity for non-diseased eyes |
| **Healthy (`No_DR`) Recall** | **98.0%** | Near-zero false-negative rate for clinical screening |

> **Diagnostic Insight:** The 98% recall and precision on `No_DR` validates the model as a reliable primary triage filter, automatically flagging non-diseased screenings with high confidence and routing ambiguous or severe cases to specialist care.

---

## 🚀 How to Run & Inference Pipeline

### 1. Environment Setup
```bash
pip install fastai torch torchvision pillow
```

### 2. Standalone Inference Script
```python
from fastai.vision.all import *

# 1. Load serialized learner
learner = load_learner('resnet34_fine_tune.pkl')

# 2. Evaluate sample fundus image
image_path = 'diabetic-retinopathy-224x224-2019-data/colored_images/Severe/91cf56d3d1af.png'
img = PILImage.create(image_path)
pred_class, pred_idx, probabilities = learner.predict(img)

print(f"Predicted Diagnosis : {pred_class}")
print(f"Confidence Score    : {probabilities[pred_idx]:.4f}")
```

---

## 🖼️ Visuals & Diagnostic Plots
![Project Preview](./preview.png)
