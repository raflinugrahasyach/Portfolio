![Preview](preview.png)

# Student Satisfaction Classification with IndoBERT

## 📌 Overview
An NLP research project fine-tuning IndoBERT for multi-class student satisfaction classification from free-text survey responses. This study explores BERT-based transfer learning for Indonesian educational feedback analysis.

## 🛠 Tech Stack
- **Language:** Python
- **Libraries:** HuggingFace Transformers, IndoBERT, PyTorch, Pandas

## 📊 Dataset
Dataset telah melalui proses *scrambling* dan anonimisasi untuk menjaga privasi, tanpa mengubah distribusi statistik utama yang relevan dengan pemodelan.

## 🚀 Methodology
1. Survey text collection and labeling (2-class & 5-class)
2. Indonesian text normalization and preprocessing
3. IndoBERT fine-tuning with custom classification head
4. Cross-validation and error analysis

## 📈 Key Results & Metrics
- 2-class Accuracy: 94.3%
- 5-class Accuracy: 87.6%
- F1-Score (macro): 86.9%

## 📁 Project Structure
```
Student_Satisfaction_IndoBERT/
├── README.md
├── IndoBERT_Kepuasan_Mahasiswa_Fixed.ipynb
├── add_selective_cell.py
├── Bismillah_TA_Lancar (1).ipynb.txt
├── cell11_debug.txt
├── cell_contents.txt
├── check_tail.py
├── clean_ambiguous_data.py
├── confusion_matrix (2).png
├── dataset_kepuasan_clean.csv
```
