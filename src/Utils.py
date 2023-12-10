import os, sys

class Utils():
    @staticmethod
    def get_abs_path(relative_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        base_path = getattr(sys, '_MEIPASS', parent_dir)
        path = os.path.join(base_path, relative_path).replace("\\", "/")
        return path

class noLogger:
    def error(msg):
        pass
    def warning(msg):
        pass
    def debug(msg):
        pass