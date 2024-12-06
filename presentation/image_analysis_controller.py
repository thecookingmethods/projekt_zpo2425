import numpy as np
from PIL import Image
from flask import request, Flask

from BLL.image_analysis_queue import ImageAnalysisQueue
from DAL.image_analysis_repository import ImageAnalysisRepository
from DAL.temporary_file_container import TemporaryFileContainer
from models.exceptions.image_analysis_not_exists import ImageAnalysisNotExists
from models.image_analysis_order import ImageAnalysisOrder


class ImageAnalysisController:
    def __init__(self,
                 repo: ImageAnalysisRepository,
                 order_queue: ImageAnalysisQueue):
        self._repo = repo
        self._order_queue = order_queue

        self.app = Flask(__name__)
        self.app.add_url_rule('/', view_func=self.get_form, methods=['GET'])
        self.app.add_url_rule('/image', view_func=self.analyze_image, methods=['POST'])
        self.app.add_url_rule('/image/<analysis_id>', view_func=self.get_analysis, methods=['GET'])

    def get_form(self):
        return ('<form action=/image method=post enctype=multipart/form-data>'
                '<input type=file name=image>'
                '<input type=submit>'
                '</form>')

    def analyze_image(self):
        if 'image' not in request.files:
            return {'error': 'brak pliku'}, 400
        file = request.files['image']
        if file.filename == '':
            return {'error': 'plik jest pusty'}, 400

        file_extension = file.filename.split('.')[-1]
        if file_extension == 'jpg':
            analysis = self._repo.create_analysis()

            temp_file_container = TemporaryFileContainer(file_extension)
            file_path = temp_file_container.get_path()
            file.save(file_path)

            image_array = np.array(Image.open(file_path))

            self._order_queue.order_analysis(ImageAnalysisOrder(image_array, analysis.id))

            return {'id': str(analysis.id) }, 200

        return {'error': 'zly format'}, 400

    def get_analysis(self, analysis_id):
        try:
            analysis = self._repo.get_analysis(int(analysis_id))
        except ImageAnalysisNotExists:
            return {'error': 'nieznane id'}, 400

        if analysis.caption is None:
            return {'info': 'analiza w toku...'}, 200

        return {'caption': analysis.caption }, 200