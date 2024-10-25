import os

from models.exceptions.image_analysis_not_exists import ImageAnalysisNotExists
from models.image_analysis import ImageAnalysis


class ImageAnalysisRepository:
    caption_file_name = "caption.txt"

    def __init__(self, db_dir):
        self._db_dir = db_dir
        os.makedirs(self._db_dir, exist_ok=True)

    def create_analysis(self) -> ImageAnalysis:
        entries_list = os.listdir(self._db_dir)
        if len(entries_list) == 0:
            new_id = 1
        else:
            sorted_entries = sorted(entries_list, key=lambda x: int(x))
            last_id = int(sorted_entries[-1])
            new_id = last_id + 1
        entry_dir = os.path.join(self._db_dir, str(new_id))
        os.makedirs(entry_dir)
        analysis = ImageAnalysis(new_id, None)

        return analysis

    def update_analysis(self, analysis: ImageAnalysis) -> None:
        entry_dir = os.path.join(self._db_dir, str(analysis.id))
        if not os.path.exists(entry_dir):
            raise ImageAnalysisNotExists
        caption_file_path = os.path.join(entry_dir, self.caption_file_name)
        with open(caption_file_path, 'w') as f:
            f.write(analysis.caption)

    def get_analysis(self, id: int) -> ImageAnalysis:
        entry_dir = os.path.join(self._db_dir, str(id))
        if not os.path.exists(entry_dir):
            raise ImageAnalysisNotExists

        caption_file_path = os.path.join(entry_dir, self.caption_file_name)
        if not os.path.exists(caption_file_path):
            caption = None
        else:
            with open(caption_file_path, 'r') as f:
                caption = f.read()

        analysis = ImageAnalysis(id, caption)
        return analysis
