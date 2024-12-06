import queue

from models.image_analysis_order import ImageAnalysisOrder


class ImageAnalysisQueue:
    def __init__(self):
        self._queue = queue.Queue()

    def order_analysis(self, order: ImageAnalysisOrder):
        self._queue.put(order)

    def get_order(self) -> ImageAnalysisOrder:
        while True:
            try:
                print('waiting for an order...')
                order: ImageAnalysisOrder = self._queue.get(block=True, timeout=10)
                print(f'got order with analysis id {order.analysis_id}')
                return order
            except queue.Empty:
                print('timeout!')
                continue

