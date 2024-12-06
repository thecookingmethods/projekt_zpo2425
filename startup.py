from BLL.caption_generator import CaptionGenerator
from BLL.image_analysis_queue import ImageAnalysisQueue
from BLL.image_analysis_service import ImageAnalysisService
from DAL.caption_generator_model_provider import CaptionGeneratorModelProvider
from DAL.image_analysis_repository import ImageAnalysisRepository
from config import Config
from presentation.image_analysis_controller import ImageAnalysisController


class Startup:
    def __init__(self, config: Config):
        self._config = config

        # DAL
        repo = ImageAnalysisRepository(config.db_dir)
        model_provider = CaptionGeneratorModelProvider(
            config.ai_model_path, config.ai_model_tokens_path)

        # BLL
        order_queue = ImageAnalysisQueue()
        caption_generator = CaptionGenerator(model_provider)

        self._analysis_service = ImageAnalysisService(caption_generator, repo, order_queue)

        # presentation
        self._controller = ImageAnalysisController(repo, order_queue)

    def run(self):
        self._analysis_service.start()
        self._controller.app.run(host=self._config.webapi_host, port=self._config.webapi_port)