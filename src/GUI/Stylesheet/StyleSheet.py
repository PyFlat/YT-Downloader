from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig
from enum import Enum

class StyleSheet(StyleSheetBase, Enum):

    SETTING_INTERFACE = "setting_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"src/GUI/Stylesheet/qss/{theme.value.lower()}/{self.value}.qss"