import threading

from BLL.caption_generator import CaptionGenerator
from BLL.image_analysis_queue import ImageAnalysisQueue
from DAL.image_analysis_repository import ImageAnalysisRepository
from models.image_analysis_order import ImageAnalysisOrder


class ImageAnalysisService:
    def __init__(self,
                 caption_generator: CaptionGenerator,
                 repo: ImageAnalysisRepository,
                 queue: ImageAnalysisQueue,
                 no_of_threads=2):

        self._caption_generator = caption_generator
        self._repo = repo
        self._queue = queue

        self._is_running = False

        self._workers = [threading.Thread(target=self._analyze, args=(i,)) for i in range(no_of_threads)]

    def start(self):
        self._is_running = True
        for worker in self._workers:
            worker.start()

    def _analyze(self, worker_id):
        print(f'worker no {worker_id} is starting...')
        while self._is_running:
            print(f'worker no {worker_id} is waiting for and order ...')
            order: ImageAnalysisOrder = self._queue.get_order()
            print(f'worker no {worker_id} got order with id {order.analysis_id} ...')
            captions = self._caption_generator.generate(order.image)
            analysis = self._repo.get_analysis(order.analysis_id)
            analysis.caption = captions
            self._repo.update_analysis(analysis)
            print(f'worker no {worker_id} finished analysis for {order.analysis_id} ...')