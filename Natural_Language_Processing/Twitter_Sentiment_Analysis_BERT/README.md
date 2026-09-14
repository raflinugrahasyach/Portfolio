

# Twitter / X Sentiment Analysis with BERT Fine-Tuning

## 📌 Overview
An NLP research project fine-tuning a multilingual BERT model for sentiment classification of Indonesian Twitter/X posts. This study explores optimal fine-tuning strategies for Indonesian social media text.

## 🛠 Tech Stack
- **Language:** Python
- **Libraries:** HuggingFace Transformers, PyTorch, Pandas, Scikit-learn

## 📊 Dataset
Dataset telah melalui proses *scrambling* dan anonimisasi untuk menjaga privasi, tanpa mengubah distribusi statistik utama yang relevan dengan pemodelan.

## 🚀 Methodology
1. Twitter dataset collection and preprocessing
2. Indonesian text normalization (slang, emoji)
3. IndoBERT / mBERT fine-tuning with AdamW optimizer
4. Sentiment classification evaluation (3-class: pos/neg/neu)

## 📈 Key Results & Metrics
- Accuracy: 91.7%
- F1-Score (macro): 90.8%
- Training Data: 185K+ tweets

## 📁 Project Structure
```
Twitter_Sentiment_Analysis_BERT/
├── README.md
├── BERT_Sentiment_Twitter.ipynb
├── dataset x.csv
├── dataset_x.csv
├── data_cleaned_labeled.csv
├── data_final_with_predictions.csv
├── update_5_BERT_Sentimen_X.ipynb
```


