from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from untitled_ui import Ui_Form
import Translator
import sys, os

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        os.chdir("language-test")
        self.strings_en = Translator.parse_keystring(open("languages/language_en.properties", "r").read())
        self.ui.pushButton.clicked.connect(self.change_language)
        self.show()

    def change_language(self):
        for key, value in self.strings_en.items():
            if '.' in key:
                method_name, attribute_name = key.split('.')
                method = getattr(getattr(self.ui, method_name), attribute_name)
                method(value)
            else:
                method = getattr(self, key)
                method(value)

if __name__ == "__main__":
    app = QApplication([])
    mw = MainWindow()
    sys.exit(app.exec())