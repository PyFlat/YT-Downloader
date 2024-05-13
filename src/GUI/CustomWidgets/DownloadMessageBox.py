
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from qfluentwidgets import MessageBoxBase, ProgressRing, TitleLabel, SubtitleLabel


class DownloadMessageBox(MessageBoxBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttonGroup.setVisible(False)
        self.setupUi()
        self.TitleLabel.setText("Please Wait...")
        self.SubtitleLabel_2.setText("Download started...")

    def setupUi(self):
        self.widget = QWidget(self.parent())
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(15, 0, 0, 0)
        self.ProgressRing = ProgressRing(self.widget)
        self.ProgressRing.setObjectName(u"ProgressRing")
        self.ProgressRing.setTextVisible(True)

        self.horizontalLayout_2.addWidget(self.ProgressRing)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.TitleLabel = TitleLabel(self.widget_2)
        self.TitleLabel.setObjectName(u"TitleLabel_2")

        self.verticalLayout.addWidget(self.TitleLabel)

        self.SubtitleLabel_2 = SubtitleLabel(self.widget_2)
        self.SubtitleLabel_2.setObjectName(u"SubtitleLabel_2")

        self.verticalLayout.addWidget(self.SubtitleLabel_2)


        self.horizontalLayout_2.addWidget(self.widget_2, 0, Qt.AlignVCenter)

        self.viewLayout.addWidget(self.widget, 0, Qt.AlignLeft)

    def updateProgress(self, progress):
        self.ProgressRing.setValue(progress)