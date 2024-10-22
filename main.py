import os
import threading

from flask import Flask, request
from keras.src.layers import TextVectorization
from werkzeug.utils import secure_filename
import keras

from model_training import (ImageCaptioningModel,TransformerEncoderBlock,
                            PositionalEmbedding, TransformerDecoderBlock,
                            LRSchedule, load_captions_data)
from test_model import custom_standardization, generate_caption

app = Flask(__name__)

model: ImageCaptioningModel = keras.models.load_model(
    './model.keras',
              custom_objects={
                  "ImageCaptioningModel": ImageCaptioningModel,
                  "TransformerEncoderBlock": TransformerEncoderBlock,
                  "PositionalEmbedding": PositionalEmbedding,
                  "TransformerDecoderBlock": TransformerDecoderBlock,
                  "LRSchedule": LRSchedule
                  })

VOCAB_SIZE = 10000
SEQ_LENGTH = 25
max_decoded_sentence_length = SEQ_LENGTH - 1

captions_mapping, text_data = load_captions_data("Flickr8k.token.txt")
vectorization = TextVectorization(
    max_tokens=VOCAB_SIZE,
    output_mode="int",
    output_sequence_length=SEQ_LENGTH,
    standardize=custom_standardization,
)
vectorization.adapt(text_data)

vocab = vectorization.get_vocabulary()
index_lookup = dict(zip(range(len(vocab)), vocab))

db_dir = './uploaded_files'
os.makedirs(db_dir, exist_ok=True)


@app.route('/', methods=['GET'])
def main():
    return ('<form action=/image method=post enctype=multipart/form-data>'
            '<input type=file name=image>'
            '<input type=submit>'
            '</form>')


@app.route('/image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return 'brak pliku'
    file = request.files['image']
    if file.filename == '':
        return 'plik jest pusty'

    if file.filename.split('.')[-1] == 'jpg':
        entries_list = os.listdir(db_dir)
        if len(entries_list) == 0:
            new_id = 1
        else:
            sorted_entries = sorted(entries_list, key=lambda x: int(x))
            last_id = int(sorted_entries[-1])
            new_id = last_id + 1
        new_id = str(new_id)
        entry_dir = os.path.join(db_dir, new_id)
        os.makedirs(entry_dir)
        file_path = os.path.join(entry_dir, 'image.jpg')
        file.save(file_path)

        thread = threading.Thread(target=analysis_fun, args=(file_path, entry_dir))
        thread.start()

        return new_id

    return 'cos poszlo nie tak'


def analysis_fun(file_path, entry_dir):
    captions = generate_caption(model, file_path, max_decoded_sentence_length, index_lookup, vectorization)
    captions_path = os.path.join(entry_dir, "captions.txt")
    with open(captions_path, 'w') as f:
        f.write(captions)

@app.route('/image/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    entry_dir = os.path.join(db_dir, analysis_id)
    if not os.path.exists(entry_dir):
        return 'nieznane id'

    captions_path = os.path.join(db_dir, analysis_id, 'captions.txt')
    if not os.path.exists(captions_path):
        return 'analiza w toku...'

    with open(captions_path, 'r') as f:
        captions = f.read()
    return captions



if __name__ == "__main__":
    app.run(host='localhost', port=8080)
