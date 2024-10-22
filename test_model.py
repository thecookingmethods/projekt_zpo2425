import time

import keras
from keras.layers import TextVectorization
import numpy as np
import tensorflow as tf
import re
import os

from model_training import \
    (ImageCaptioningModel,
     TransformerEncoderBlock,
     PositionalEmbedding,
     TransformerDecoderBlock,
     LRSchedule,
     load_captions_data)


def main():
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

    img_path = 'test.jpg'
    captions = generate_caption(model, img_path, max_decoded_sentence_length, index_lookup, vectorization)

    print(captions)


def custom_standardization(input_string):
    strip_chars = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
    strip_chars = strip_chars.replace("<", "")
    strip_chars = strip_chars.replace(">", "")
    lowercase = tf.strings.lower(input_string)
    return tf.strings.regex_replace(lowercase, "[%s]" % re.escape(strip_chars), "")


def generate_caption(caption_model, sample_img, max_decoded_sentence_length, index_lookup, vectorization):
    print('analyzing image...')
    analysis_start = time.time()
    sample_img = decode_and_resize(sample_img)
    #plt.imshow(img)
    #plt.show()

    # Pass the image to the CNN
    img = tf.expand_dims(sample_img, 0)
    img = caption_model.cnn_model(img)

    # Pass the image features to the Transformer encoder
    encoded_img = caption_model.encoder(img, training=False)

    # Generate the caption using the Transformer decoder
    decoded_caption = "<start> "
    for i in range(max_decoded_sentence_length):
        tokenized_caption = vectorization([decoded_caption])[:, :-1]
        mask = tf.math.not_equal(tokenized_caption, 0)
        predictions = caption_model.decoder(
            tokenized_caption, encoded_img, training=False, mask=mask
        )
        sampled_token_index = np.argmax(predictions[0, i, :])
        if sampled_token_index not in index_lookup:
            sampled_token = ''
        else:
            sampled_token = index_lookup[sampled_token_index]
        if sampled_token == "<end>":
            break
        decoded_caption += " " + sampled_token

    decoded_caption = decoded_caption.replace("<start> ", "")
    decoded_caption = decoded_caption.replace(" <end>", "").strip()
    time.sleep(8)
    print(f'analysis finished in {time.time() - analysis_start}')
    return decoded_caption


def decode_and_resize(img_path):
    IMAGE_SIZE = (299, 299)
    img = tf.io.read_file(img_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMAGE_SIZE)
    img = tf.image.convert_image_dtype(img, tf.float32)
    return img


if __name__ == "__main__":
    main()
