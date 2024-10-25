import io
import os
import tempfile
import threading

from flask import Flask, request
from keras.src.layers import TextVectorization
from werkzeug.utils import secure_filename
import keras

from DAL.image_analysis_repository import ImageAnalysisRepository
from DAL.temporary_file_container import TemporaryFileContainer
from model_training import (ImageCaptioningModel,TransformerEncoderBlock,
                            PositionalEmbedding, TransformerDecoderBlock,
                            LRSchedule, load_captions_data)
from models.exceptions.image_analysis_not_exists import ImageAnalysisNotExists
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
repo = ImageAnalysisRepository(db_dir)


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

    file_extension = file.filename.split('.')[-1]
    if file_extension == 'jpg':
        analysis = repo.create_analysis()

        temp_file_container = TemporaryFileContainer(file_extension)
        file_path = temp_file_container.get_path()
        file.save(file_path)

        thread = threading.Thread(target=analysis_fun, args=(temp_file_container, analysis.id))
        thread.start()

        return str(analysis.id)

    return 'cos poszlo nie tak'


def analysis_fun(temp_file_container, id: int):
    file_path = temp_file_container.get_path()
    captions = generate_caption(model, file_path, max_decoded_sentence_length, index_lookup, vectorization)
    analysis = repo.get_analysis(id)
    analysis.caption = captions
    repo.update_analysis(analysis)


@app.route('/image/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    try:
        analysis = repo.get_analysis(int(analysis_id))
    except ImageAnalysisNotExists:
        return 'nieznane id'

    if analysis.caption is None:
        return 'analiza w toku...'

    return analysis.caption



if __name__ == "__main__":
    app.run(host='localhost', port=8080)
    #   https://github.com/thecookingmethods/projekt_zpo2425
