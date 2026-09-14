# 🛒 E-Commerce App Feedback Mining & Sentiment Classification: IndoBERT Pseudo-Labeling vs. SVM and Naive Bayes

## 📖 Overview & Product Analytics Value
Leading mobile e-commerce platforms (such as Shopee) process tens of thousands of customer reviews every month on app marketplaces like the Google Play Store. Unstructured app reviews contain direct signals regarding checkout errors, logistics delays, promotional voucher failures, and UI latency. For mobile product managers and engineering teams, automated sentiment classification and topic extraction serve as early-warning systems to prioritize software bug fixes before user churn escalates.

This project delivers an end-to-end e-commerce review mining pipeline. The methodology combines **deep contextual pseudo-labeling using IndoBERT** with **unsupervised topic clustering** to isolate core complaint themes, subsequently training lightweight production-ready classifiers (**Multinomial Naive Bayes** and **Support Vector Machines**) capable of sub-millisecond sentiment scoring.

---

## 🔤 Text Preprocessing & Topic Modeling Pipeline
The scraped dataset (`shopee_reviews_sentiment_analysis_dataset.csv`) undergoes a standardized cleaning and feature extraction sequence:

1. **Orthographic Cleaning & Tokenization**:
   - Stripped emojis, HTML tags, punctuation artifacts, and redundant whitespace.
   - Filtered domain-agnostic Indonesian stopwords while preserving critical negation modifiers (e.g., *"tidak"*, *"belum"*).
2. **Unsupervised Topic Discovery**:
   - Clustered vocabulary co-occurrences to identify predominant consumer grievance clusters:
     - **Topic 1 — App Performance & Latency**: Complaints regarding slow load times, crashes, and memory bloat.
     - **Topic 2 — Checkout & Payment Systems**: Friction in payment gateway verification and digital wallet balance synchronization.
     - **Topic 3 — Logistics & Courier Tracking**: Late parcel deliveries, un-updated tracking manifests, and courier conduct.
     - **Topic 4 — Promotion & Voucher Mechanics**: Expired vouchers, free shipping coupon caps, and promotional code invalidation.
3. **TF-IDF Vector Space Construction**:
   - Fitted `TfidfVectorizer` to extract salient n-gram term frequencies, serialized via `joblib` for production deployment.

---

## 🧠 Model Architecture & Comparative Strategy
The modeling framework follows a hybrid knowledge distillation approach:

1. **Deep Semantic Labeling (IndoBERT)**:
   - Utilized pre-trained `indobenchmark/indobert-base-p1` to generate high-confidence pseudo-labels across the uncurated review corpus, avoiding costly manual human annotation.
2. **Production Classifier Training**:
   - **Multinomial Naive Bayes (`naive_bayes_model.pkl`)**: Probabilistic baseline providing high execution throughput for streaming pipelines.
   - **Support Vector Machine (`svm_model.pkl`)**: Convex optimization maximizing the linear margin separating sentiment hyperplanes in high-dimensional TF-IDF space.

---

## 📊 Key Results & Empirical Metrics

| Classifier Model | Feature Representation | Test Accuracy | Macro Precision | Macro Recall | Inference Latency |
|------------------|------------------------|---------------|-----------------|--------------|-------------------|
| **Multinomial Naive Bayes** | TF-IDF | **87.17%** | 86.8% | 87.0% | `< 5 ms` |
| **Support Vector Machine (SVM)** | TF-IDF | **87.33%** | **87.4%** | **87.2%** | `< 8 ms` |

```python
import joblib

# Production inference demonstration
loaded_svm = joblib.load('svm_model.pkl')
loaded_vec = joblib.load('vectorizer_svm.pkl')

sample_review = "aplikasi lemot banget setelah update, pas checkout sering error!"
clean_vec = loaded_vec.transform([sample_review])
prediction = loaded_svm.predict(clean_vec)

print(f"Predicted Sentiment : {prediction[0]}")  # Output: negative
```

---

## 🚀 How to Run & Reproduce

### 1. Requirements
```bash
pip install pandas scikit-learn nltk matplotlib joblib jupyter
```

### 2. Execute Research Notebook
```bash
jupyter notebook shopee_reviews_sentiment_analysis.ipynb
```

---

## 🖼️ Accuracy Comparison & Topic Distributions
![Project Preview](./preview.png)
