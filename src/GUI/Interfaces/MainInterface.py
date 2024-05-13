from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QStackedWidget,
    QVBoxLayout, QWidget)
from qfluentwidgets import (LineEdit, PushButton)
class MainInterface(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setObjectName("MainInterface")
        Form = self
        Form.resize(747, 410)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.LineEdit = LineEdit(self.widget)
        self.LineEdit.setObjectName(u"LineEdit")
        self.LineEdit.setAlignment(Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.LineEdit)
        self.PushButton = PushButton(self.widget)
        self.PushButton.setObjectName(u"PushButton")
        self.horizontalLayout.addWidget(self.PushButton)
        self.verticalLayout.addWidget(self.widget)
        self.stackedWidget = QStackedWidget(Form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.horizontalLayout_3 = QHBoxLayout(self.page)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout.addWidget(self.stackedWidget)
        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(Form)
    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.LineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Enter the URL of the video or playlist, or type in a search term.", None))
        self.PushButton.setText(QCoreApplication.translate("Form", u"Search", None))
        self.PushButton.setShortcut(QCoreApplication.translate("Form", u"Return", None))