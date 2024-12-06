import numpy as np
from PIL import Image
from keras.src.layers import TextVectorization

from DAL.caption_generator_model_provider import CaptionGeneratorModelProvider
from DAL.temporary_file_container import TemporaryFileContainer
from test_model import custom_standardization, generate_caption


class CaptionGenerator:
    VOCAB_SIZE = 10000
    SEQ_LENGTH = 25

    def __init__(self, model_provider: CaptionGeneratorModelProvider):
        self._model = model_provider.model

        self._max_decoded_sentence_length = self.SEQ_LENGTH - 1

        self._vectorization = TextVectorization(
            max_tokens=self.VOCAB_SIZE,
            output_mode="int",
            output_sequence_length=self.SEQ_LENGTH,
            standardize=custom_standardization,
        )

        text_data = model_provider.text_data
        self._vectorization.adapt(text_data)

        vocab = self._vectorization.get_vocabulary()
        self._index_lookup = dict(zip(range(len(vocab)), vocab))

    def generate(self, image_array: np.ndarray):
        file_path = TemporaryFileContainer('jpg').get_path()
        Image.fromarray(image_array).save(file_path)
        caption = generate_caption(self._model, file_path, self._max_decoded_sentence_length,
                                   self._index_lookup, self._vectorization)
        return caption