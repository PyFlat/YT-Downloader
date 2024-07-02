import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qfluentwidgets import ToolTip, ToolTipPosition, isDarkTheme, themeColor
from qfluentwidgets.common.overload import singledispatchmethod
from qfluentwidgets.components.widgets.slider import SliderHandle


class RangeSlider(QSlider):
    """A range slider with two handles"""

    lowerValueChanged = Signal(int)
    upperValueChanged = Signal(int)

    @singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._postInit()

    @__init__.register
    def _(self, parent: QWidget = None):
        super().__init__(Qt.Horizontal, parent=parent)
        self._postInit()

    def _postInit(self):
        self.lowerHandle = SliderHandle(self)

        self.toolTipLower = ToolTip("", self.parent())
        self.toolTipLower.setDuration(2000)

        self.upperHandle = SliderHandle(self)

        self.toolTipUpper = ToolTip("", self.parent())
        self.toolTipUpper.setDuration(2000)

        self._pressedPos = QPoint()
        self._lowerValue = self.minimum()
        self._upperValue = self.maximum()
        self._lowerHandlePressed = False
        self._upperHandlePressed = False
        self._rangePressed = False
        self.setOrientation(self.orientation())

        self.lowerHandle.pressed.connect(self.lowerHandlePressed)
        self.upperHandle.pressed.connect(self.upperHandlePressed)
        self.lowerHandle.released.connect(self.handleReleased)
        self.upperHandle.released.connect(self.handleReleased)
        self.lowerValueChanged.connect(self.lowerHandleMoved)
        self.upperValueChanged.connect(self.upperHandleMoved)
        self.valueChanged.connect(self._adjustHandlePos)

    def setMinimum(self, int):
        super().setMinimum(int)
        self._lowerValue = int
        self._adjustHandlePos()

    def setMaximum(self, int):
        super().setMaximum(int)
        self._upperValue = int
        self._adjustHandlePos()

    def setRange(self, min: int = 0, max: int = 99) -> None:
        self.setMinimum(min)
        self.setMaximum(max)

    def getRange(self) -> tuple[int, int]:
        min = self.minimum()
        max = self.maximum()

        return min, max

    def value(self) -> tuple[int, int]:
        return self._lowerValue, self._upperValue

    def setValue(self, start: int = 0, end: int = 1):
        self._lowerValue = start
        self._upperValue = end

        self._adjustHandlePos()

    def setEnabled(self, arg: bool):
        super().setEnabled(arg)
        if arg:
            self.lowerHandle.setVisible(True)
            self.upperHandle.setVisible(True)
        else:
            self.lowerHandle.setVisible(False)
            self.upperHandle.setVisible(False)

    def setOrientation(self, orientation: Qt.Orientation) -> None:
        super().setOrientation(orientation)
        self.setMinimumHeight(22)

    def lowerHandlePressed(self):
        self._lowerHandlePressed = True

    def upperHandlePressed(self):
        self._upperHandlePressed = True

    def handleReleased(self):
        self._lowerHandlePressed = False
        self._upperHandlePressed = False
        self._rangePressed = False

    def lowerHandleMoved(self, value):
        self.lowerHandle.move(self._valueToPos(value), 0)
        self.showToolTip()
        self.update()

    def upperHandleMoved(self, value):
        self.upperHandle.move(self._valueToPos(value), 0)
        self.showToolTip()
        self.update()

    def showToolTip(self):
        self.toolTipLower.adjustPos(self.lowerHandle, ToolTipPosition.TOP)
        self.toolTipLower.setText(str(self._lowerValue))

        self.toolTipUpper.adjustPos(self.upperHandle, ToolTipPosition.TOP)
        self.toolTipUpper.setText(str(self._upperValue))

        ToolTip.show(self.toolTipLower)
        ToolTip.show(self.toolTipUpper)

    def mousePressEvent(self, e: QMouseEvent):
        self._pressedPos = e.position().toPoint()
        val = self._posToValue(self._pressedPos)
        lower_pos = self._valueToPos(self._lowerValue)
        upper_pos = self._valueToPos(self._upperValue)

        if lower_pos > self._pressedPos.x() or self._pressedPos.x() > upper_pos:

            if abs(val - self._lowerValue) < abs(val - self._upperValue):
                if abs(self._pressedPos.x() - lower_pos) < 1:
                    self._lowerHandlePressed = True
                else:
                    self._lowerValue = val
                    self.lowerValueChanged.emit(self._lowerValue)
            else:
                if abs(self._pressedPos.x() - upper_pos) < 1:
                    self._upperHandlePressed = True
                else:
                    self._upperValue = val
                    self.upperValueChanged.emit(self._upperValue)

        else:
            self._rangePressed = True
            self._rangeOffset = self._pressedPos.x() - lower_pos

        self.update()

    def mouseMoveEvent(self, e: QMouseEvent):
        val = self._posToValue(e.position().toPoint())
        if self._lowerHandlePressed:
            if val < self._upperValue:
                if val < self.minimum():
                    return
                self._lowerValue = val
                self.lowerValueChanged.emit(self._lowerValue)
        elif self._upperHandlePressed:
            if val > self._lowerValue:
                if val > self.maximum():
                    return
                self._upperValue = val
                self.upperValueChanged.emit(self._upperValue)
        elif self._rangePressed:
            delta = val - self._posToValue(self._pressedPos)
            new_lower = self._lowerValue + delta
            new_upper = self._upperValue + delta

            if new_lower < self.minimum():
                delta = self.minimum() - self._lowerValue
            elif new_upper > self.maximum():
                delta = self.maximum() - self._upperValue

            self._lowerValue += delta
            self._upperValue += delta
            self.lowerValueChanged.emit(self._lowerValue)
            self.upperValueChanged.emit(self._upperValue)
            self._pressedPos = e.position().toPoint()

        self.update()

    def mouseReleaseEvent(self, e):
        self._lowerHandlePressed = False
        self._upperHandlePressed = False
        self._rangePressed = False

    @property
    def grooveLength(self):
        l = self.width()
        return l - self.lowerHandle.width()

    def _adjustHandlePos(self):
        total = max(self.maximum() - self.minimum(), 1)
        deltaLower = int(
            (self._lowerValue - self.minimum()) / total * self.grooveLength
        )
        deltaUpper = int(
            (self._upperValue - self.minimum()) / total * self.grooveLength
        )

        self.lowerHandle.move(deltaLower, 0)
        self.upperHandle.move(
            deltaUpper - self.upperHandle.width() + self.lowerHandle.width(), 0
        )

    def _posToValue(self, pos: QPoint):
        pd = self.lowerHandle.width() / 2
        gs = max(self.grooveLength, 1)
        v = pos.x()
        return int((v - pd) / gs * (self.maximum() - self.minimum()) + self.minimum())

    def _valueToPos(self, value):
        total = max(self.maximum() - self.minimum(), 1)
        groove_pos = (int(value) - self.minimum()) / total * self.grooveLength
        groove_pos = max(0, min(groove_pos, self.grooveLength))
        return int(groove_pos)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            QColor(255, 255, 255, 115) if isDarkTheme() else QColor(0, 0, 0, 100)
        )

        self._drawHorizonGroove(painter)

    def _drawHorizonGroove(self, painter: QPainter):
        w, r = self.width(), self.lowerHandle.width() / 2
        groove_start = r
        groove_end = w - r * 2

        selected_start = self._valueToPos(self._lowerValue)
        selected_end = self._valueToPos(self._upperValue)

        if selected_start > selected_end:
            selected_start, selected_end = selected_end, selected_start

        painter.drawRoundedRect(QRectF(groove_start, r - 2, groove_end, 4), 2, 2)

        if self.maximum() - self.minimum() == 0:
            return
        if self.isEnabled():
            painter.setBrush(themeColor())
            painter.drawRoundedRect(
                QRectF(
                    groove_start + selected_start,
                    r - 2,
                    selected_end - selected_start,
                    4,
                ),
                2,
                2,
            )

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._adjustHandlePos()
