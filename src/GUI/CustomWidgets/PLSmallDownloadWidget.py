from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, Qt
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout
from qfluentwidgets import StrongBodyLabel


class ElidedLabel(StrongBodyLabel):
    def paintEvent(self, event):
        painter = QPainter(self)

        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)


class PLSmallDownloadWidget(QFrame):
    def __init__(self, parent=None, title: str = "", uploader: str = ""):
        super().__init__(parent)
        self.setFixedSize(650, 35)

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setContentsMargins(16, 8, 16, 8)
        self.channel_label = ElidedLabel(title, self)
        self.horizontalLayout.addWidget(self.channel_label)
        self.StrongBodyLabel = StrongBodyLabel(f"by {uploader}", self)
        self.horizontalLayout.addWidget(
            self.StrongBodyLabel, 0, Qt.AlignmentFlag.AlignRight
        )

        self.progress = 0

        self.setAutoFillBackground(True)

    def set_progress(self, value: float):
        """
        Set the progress value and update the widget.
        :param value: Integer from 0 to 100 indicating the progress percentage.
        """
        self.progress = max(0, min(100, value))
        self.update()

    def add_shadow_effect(self, color: QColor = QColor(255, 255, 255, 150)):
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(20)
        glow.setXOffset(0)
        glow.setYOffset(0)
        glow.setColor(color)
        self.setGraphicsEffect(glow)

    def paintEvent(self, event):
        """
        Custom paint event to draw the background color based on the progress value.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        base_color = QColor(0, 0, 0, 64)
        progress_color = QColor(255, 255, 255, 32)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), 15, 15)
        painter.fillPath(path, base_color)

        progress_width = int(self.width() * self.progress / 100)

        if progress_width > 0:
            progress_path = QPainterPath()
            progress_rect = QRect(0, 0, progress_width, self.height())
            progress_path.addRoundedRect(progress_rect, 15, 15)
            painter.fillPath(progress_path, progress_color)
