from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)
from qfluentwidgets import (BodyLabel, ProgressBar, PushButton, StrongBodyLabel,
    SubtitleLabel)
class DownloadWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setObjectName("DownloadWidget")
        Form = self
        Form.resize(861, 254)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.SubtitleLabel = SubtitleLabel(self.widget)
        self.SubtitleLabel.setObjectName(u"SubtitleLabel")
        self.SubtitleLabel.setTextFormat(Qt.RichText)
        self.SubtitleLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.SubtitleLabel)
        self.StrongBodyLabel = StrongBodyLabel(self.widget)
        self.StrongBodyLabel.setObjectName(u"StrongBodyLabel")
        self.verticalLayout.addWidget(self.StrongBodyLabel)
        self.verticalLayout_2.addWidget(self.widget)
        self.widget_3 = QWidget(Form)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setSpacing(25)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.StrongBodyLabel_2 = StrongBodyLabel(self.widget_3)
        self.StrongBodyLabel_2.setObjectName(u"StrongBodyLabel_2")
        self.horizontalLayout_2.addWidget(self.StrongBodyLabel_2)
        self.BodyLabel_2 = BodyLabel(self.widget_3)
        self.BodyLabel_2.setObjectName(u"BodyLabel_2")
        self.horizontalLayout_2.addWidget(self.BodyLabel_2)
        self.BodyLabel_3 = BodyLabel(self.widget_3)
        self.BodyLabel_3.setObjectName(u"BodyLabel_3")
        self.horizontalLayout_2.addWidget(self.BodyLabel_3)
        self.verticalLayout_2.addWidget(self.widget_3, 0, Qt.AlignLeft)
        self.widget_2 = QWidget(Form)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setSpacing(25)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ProgressBar = ProgressBar(self.widget_2)
        self.ProgressBar.setObjectName(u"ProgressBar")
        self.ProgressBar.setMinimumSize(QSize(0, 6))
        self.ProgressBar.setValue(69)
        self.ProgressBar.setTextVisible(True)
        self.horizontalLayout.addWidget(self.ProgressBar)
        self.BodyLabel = BodyLabel(self.widget_2)
        self.BodyLabel.setObjectName(u"BodyLabel")
        self.horizontalLayout.addWidget(self.BodyLabel)
        self.PushButton = PushButton(self.widget_2)
        self.PushButton.setObjectName(u"PushButton")
        self.horizontalLayout.addWidget(self.PushButton)
        self.PushButton_2 = PushButton(self.widget_2)
        self.PushButton_2.setObjectName(u"PushButton_2")
        self.horizontalLayout.addWidget(self.PushButton_2)
        self.verticalLayout_2.addWidget(self.widget_2)
        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)
    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Frame", None))
        self.SubtitleLabel.setText(QCoreApplication.translate("Form", u" TWILIGHT OF THE GODS | Epic Dark Dramatic Music \u2013 Best Epic Heroic Orchestral Music ", None))
        self.StrongBodyLabel.setText(QCoreApplication.translate("Form", u"by Epic Music VN", None))
        self.StrongBodyLabel_2.setText(QCoreApplication.translate("Form", u"Status: Downloading...", None))
        self.BodyLabel_2.setText(QCoreApplication.translate("Form", u"Format: Video/mp4", None))
        self.BodyLabel_3.setText(QCoreApplication.translate("Form", u"Quality: 1080p/Best Audio", None))
        self.BodyLabel.setText(QCoreApplication.translate("Form", u"69% / 84 mb - 00:28 left", None))
        self.PushButton.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.PushButton_2.setText(QCoreApplication.translate("Form", u"Pause", None))