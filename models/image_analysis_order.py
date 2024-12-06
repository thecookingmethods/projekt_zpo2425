import numpy as np


class ImageAnalysisOrder:
    def __init__(self, image: np.ndarray, analysis_id: int):
        self.image = image
        self.analysis_id = analysis_id
