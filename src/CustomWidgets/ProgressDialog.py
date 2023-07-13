from PySide6.QtGui import Qt
from PySide6.QtWidgets import QProgressDialog

class ProgressDialog(QProgressDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Download Window')
        self.setModal(True)
        self.setCancelButton(None)
        self.setFixedWidth(250)
        self.setLabelText(f"Downloading {name}")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setMinimum(0)
        self.setMaximum(101)

    def update_progress(self, progress):
        self.setValue(progress)