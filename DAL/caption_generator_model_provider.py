import keras

from model_training import (ImageCaptioningModel,TransformerEncoderBlock,
                            PositionalEmbedding, TransformerDecoderBlock,
                            LRSchedule, load_captions_data)

class CaptionGeneratorModelProvider:
    def __init__(self, model_path, model_tokens_path):
        self.model: ImageCaptioningModel = keras.models.load_model(
            model_path,
            custom_objects={
                "ImageCaptioningModel": ImageCaptioningModel,
                "TransformerEncoderBlock": TransformerEncoderBlock,
                "PositionalEmbedding": PositionalEmbedding,
                "TransformerDecoderBlock": TransformerDecoderBlock,
                "LRSchedule": LRSchedule
            })

        _, self.text_data = load_captions_data(model_tokens_path)
