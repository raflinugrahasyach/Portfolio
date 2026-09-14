![Preview](./preview.png)

# Image Classification using CNN & VGG16 Transfer Learning

## 📌 Overview
A deep learning research project exploring image classification through Convolutional Neural Networks (CNN) and transfer learning with the VGG16 architecture. The study investigates the effect of fine-tuning pre-trained ImageNet weights on a custom dataset.

## 🛠 Tech Stack
- **Language:** Python
- **Libraries:** TensorFlow/Keras, NumPy, Matplotlib, OpenCV

## 📊 Dataset
Dataset telah melalui proses *scrambling* dan anonimisasi untuk menjaga privasi, tanpa mengubah distribusi statistik utama yang relevan dengan pemodelan.

## 🚀 Methodology
1. Data Augmentation & Preprocessing (ImageDataGenerator)
2. Baseline CNN architecture design and training
3. Transfer Learning with VGG16 (frozen → unfrozen layers)
4. Hyperparameter tuning and performance evaluation

## 📈 Key Results & Metrics
- Validation Accuracy: 92.4%
- F1-Score (macro): 91.8%
- Training Epochs: 50 (with early stopping)

## 📁 Project Structure
```
Image_Classification_CNN_VGG16/
├── README.md
├── CNN_VGG16_Classification.ipynb
├── developer-research_project-cnn-vgg.ipynb
```

