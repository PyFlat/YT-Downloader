from qfluentwidgets import *

class Config(QConfig):
    enableMinimizeAsTray = ConfigItem("Preferences", "EnableMinimizeAsTray", False, BoolValidator())
    enableShowOnStartup = ConfigItem("Preferences", "EnableShowOnStartup", False, BoolValidator())
    enableStartWithWindows = ConfigItem("Preferences", "EnableStartWithWindows", False, BoolValidator())


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('src/Config/config.json', cfg)