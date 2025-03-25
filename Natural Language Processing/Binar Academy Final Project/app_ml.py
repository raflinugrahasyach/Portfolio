from flask import Flask, jsonify
import re
import time
import numpy as np
import pandas as pd
import json
import pickle

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from


from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import load_model

from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report

#### flask
app = Flask(__name__)


# Menggunakan kamus kata gaul Salsabila
with open("_json_colloquial-indonesian-lexicon.txt") as f:
    kamus_alay = f.read()
# Rekonstruksi kamus_alay sebagai 'dict'
lookp_dict = json.loads(kamus_alay)
import re

def text_cleaning(text):

    # Lowercase the text
    text = text.lower()

    # Define the regex pattern for removing HTML tags
    TAG_RE = re.compile(r'<[^>]+>')

    # Remove HTML tags
    text = TAG_RE.sub('', text)

    # Remove emoji
    emoji_pattern = re.compile("["  
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002580-\U00002BEF"  # Chinese characters
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    # Remove usernames (@), hashtags (#), and URLs (https://)
    text = re.sub(r"(@\w+|#\w+|https?://\S+)", "", text)

    # Remove punctuations and numbers
    text = re.sub('[^a-zA-Z]', ' ', text)

    # Remove repeated characters (e.g., yesss -> yes)
    text = re.sub(r"([A-Za-z])\1{2,}", r"\1", text)

    # Remove single characters
    text = re.sub(r"\s+[a-zA-Z]\s+", ' ', text)

    # Remove excess spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove stopwords
    # memanfaatkan modul stopwords NLTK untuk menggunakan stopwords kustom
    # stop_word = stopwords.words('indonesian')
    # text = ' '.join([word for word in text.split() if word not in stop_word])

    return text

# load model lstm
file = open("tokenizer_lstm.pickle",'rb')
tokenizer_lstm = pickle.load(file)
file.close()
model_lstm = load_model('model_lstm.h5')

# load model mlp
file = open('tfidf_vectorizer_mlp.pkl', 'rb')
vectorizer = pickle.load(file) 
file.close()

file = open('model_mlp.pkl', 'rb')
model_mlp = pickle.load(file) 
file.close()

#sentiment
sentiment = ['negative', 'neutral', 'positive']


###swager
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Kelompok 4-Platinum Challange API'),
    # 'version': LazyString(lambda: '1.0.0'),
    # 'description': LazyString(lambda: 'Dokumentasi API'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)

###body api
@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'data': "Hello World"
    }
    return jsonify(json_response)


@swag_from("docs/text_mlp.yml", methods=['POST'])
@app.route('/text_mlp', methods=['POST'])
def input_text_mlp():
    input_text = request.form.get('text')
    clean_text = text_cleaning(input_text)
    
    # Transform input text using the pre-trained vectorizer
    text_vector = vectorizer.transform([clean_text])

    # Predict sentiment
    prediction = model_mlp.predict(text_vector)
    probability = model_mlp.predict_proba(text_vector)

    # Determine sentiment
    polarity = sentiment[prediction[0]]

    output = {
        "input_text": input_text,
        "cleaned_text": clean_text,
        "sentiment": polarity,
        "probability": np.max(probability).item()
    }

    return jsonify(output)

@swag_from("docs/text_lstm.yml", methods=['POST'])
@app.route('/text_lstm', methods=['POST'])
def input_text_lstm():
    t0 = time.time()
    input_text = request.form.get('text')
    text_clean = text_cleaning(input_text)
    predicted = tokenizer_lstm.texts_to_sequences([text_clean])
    guess = pad_sequences(predicted, maxlen=85)

    prediction = model_lstm.predict(guess)
    polarity = np.argmax(prediction[0])

    json_response = {
        'text_input': input_text,
        'text_clean': text_clean,
        'sentiment': sentiment[polarity],
        'probability': str(np.max(prediction))
    }
    print(f'Done. ({time.time() - t0:.3f}s)')
    return jsonify(json_response)

@swag_from("docs/file_lstm.yml", methods=['POST'])
@app.route('/file_lstm', methods=['POST'])
def input_file_lstm():
    t0 = time.time()
    data = request.files.getlist('file')[0]
    df = pd.read_csv(data)
    col_name = df.columns

    list_result = []
    for text in df[col_name[0]]:
        data_uper = text_cleaning(text)
        predicted = tokenizer_lstm.texts_to_sequences([data_uper])
        guess = pad_sequences(predicted, maxlen=85)

        prediction = model_lstm.predict(guess)
        polarity = np.argmax(prediction[0])

        result = {
            'text_input': text,
            'text_clean': data_uper,
            'sentiment': sentiment[polarity],
            'probability': str(np.max(prediction))
            }
        list_result.append(result)

    json_response = {
        'result file': list_result
        }

    print(f'Done. ({time.time() - t0:.3f}s)')
    return jsonify(json_response)


@swag_from("docs/file_mlp.yml", methods=['POST'])
@app.route('/file_mlp', methods=['POST'])
def input_file_mlp():
    data = request.files.getlist('file')[0]
    df = pd.read_csv(data)

    # List untuk menyimpan hasil
    results = []

    # Proses setiap baris dalam file CSV
    for index, row in df.iterrows():
        input_text = row['content'] 
        cleaned_text = text_cleaning(input_text)
        text_vector = vectorizer.transform([cleaned_text])
        prediction = model_mlp.predict(text_vector)
        probability = model_mlp.predict_proba(text_vector)
        polarity = sentiment[prediction[0]]

        # Buat dictionary untuk setiap hasil
        result = {
            "input_text": input_text,
            "cleaned_text": cleaned_text,
            "sentiment": polarity,
            "probability": np.max(probability).item()  
        }

        results.append(result)

    output_json = json.dumps(results, indent=4)

    return output_json
    
    

##running api
if __name__ == '__main__':
   app.run()