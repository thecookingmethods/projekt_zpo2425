import os
import random
import tempfile
import time


class TemporaryFileContainer:
    def __init__(self, format):
        self._format = format
        self._path = None

    def get_path(self):
        if self._path is None:
            tmp_dir = tempfile.gettempdir()
            tmp_file_name = f'{time.time_ns()}_{random.randint(0, 99999999)}.{self._format}'
            path = os.path.join(tmp_dir, tmp_file_name)
            self._path = path
        return self._path

    def __del__(self):
        print(f'usuwam plik {self._path}')
        if self._path is None and os.path.exists(self._path):
            os.remove(self._path)
