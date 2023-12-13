import os, sys
import logging
from datetime import datetime, timedelta

class Logger():
    def __init__(self, logs_folder, log_level=logging.INFO):
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
        self.remove_old_log_files(logs_folder)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        current_datetime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        log_file = os.path.join(logs_folder, f'log-{current_datetime}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.addHandler(file_handler)

        sys.stdout = self.StreamLogger(self.logger, logging.INFO)
        sys.stderr = self.StreamLogger(self.logger, logging.ERROR)

        sys.excepthook = self.exception_hook

    def set_log_level(self, log_level):
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(log_level)

    def remove_old_log_files(self, logs_folder, days_to_keep=14):
        current_datetime = datetime.now()
        for file_name in os.listdir(logs_folder):
            file_path = os.path.join(logs_folder, file_name)
            if os.path.isfile(file_path):
                file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if current_datetime - file_creation_time > timedelta(days=days_to_keep):
                    os.remove(file_path)

    def exception_hook(self, exc_type, exc_value, traceback):
        self.logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, traceback))

    class StreamLogger:
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level
            self.line_buffer = []

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.level, line.rstrip())

        def flush(self):
            pass