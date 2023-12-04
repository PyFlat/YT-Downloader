import os
import logging
from datetime import datetime

class Logger():
    def __init__(self, log_level=logging.INFO):
        logs_folder = 'logs'
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        current_datetime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        log_file = os.path.join(logs_folder, f'log-{current_datetime}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def set_log_level(self, log_level):
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(log_level)