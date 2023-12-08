from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import Qt
from PySide6.QtCore import QSize, QTimer

class SLabel(QLabel):
    def __init__(self, entry, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.searching_btn = entry
        self.setText("Loading...")
        self.setMinimumSize(QSize(325, 183))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setObjectName("search_labels")
        self.setScaledContents(True)
        self.setMouseTracking(True)
    def enterEvent(self, event):
        self.geo = self.geometry()
        self.geo2 = self.geo.adjusted(-10,-10,10,10)
        self.raise_()
        if not self.searching_btn.isEnabled():
            return
        self.setGeometry(self.geo2)
    def leaveEvent(self, event):
        if self.geometry() == self.geo2:
            self.setGeometry(self.geo)