
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class CustomTableWidget(QTableWidget):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setPen(QPen(QColor(Qt.white), 3, Qt.SolidLine))
        last_column = self.columnCount() - 1
        for row in range(self.rowCount()):
            rect = self.visualRect(self.model().index(row, 0))
            rect2 = self.visualRect(self.model().index(row, last_column))
            painter.drawLine(rect2.topRight(), rect2.bottomRight())
            painter.drawLine(rect.topLeft(), rect.bottomLeft())
        last_row = self.rowCount() - 1
        if last_row < 0: return
        for column in range(self.columnCount()):
            rect = self.visualRect(self.model().index(last_row, column))
            painter.setPen(QPen(QColor(Qt.white), 3, Qt.SolidLine))
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())