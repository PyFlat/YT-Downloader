from src.GUI.Icons.Icons import CustomIcons
from src.Config.Config import cfg
from qfluentwidgets import (ScrollArea, ExpandLayout, SettingCardGroup,
                            OptionsSettingCard, CustomColorSettingCard,
                            SwitchSettingCard,
                            setTheme, setThemeColor)
from qfluentwidgets import FluentIcon as FIF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel
from src.GUI.Stylesheet.StyleSheet import StyleSheet

class SettingInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("Settings", self)

        self.personalGroup = SettingCardGroup("Personalization", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "Application theme",
            "Change the appearance of the application",
            texts=[
                "Light", "Dark",
                "Use system setting"
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            "Theme color",
            "Change the theme color of the application",
            self.personalGroup
        )

        self.preferencesGroup = SettingCardGroup("Preferences", self.scrollWidget)
        self.minimizeAsTray =  SwitchSettingCard(
            icon = FIF.MINIMIZE,
            title = "System Tray",
            content = "Minimize application to system tray instead of exiting",
            configItem = cfg.enableMinimizeAsTray
        )
        self.showOnStartup =  SwitchSettingCard(
            icon = FIF.UP,
            title = "Show on Startup",
            content = "Shows the app instead of running in the background on startup",
            configItem = cfg.enableShowOnStartup
        )
        self.startWithWindows =  SwitchSettingCard(
            icon = CustomIcons.VIDEO,
            title = "Start with Windows",
            content = "Launch the application upon Windows startup",
            configItem = cfg.enableStartWithWindows
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")

        StyleSheet.SETTING_INTERFACE.apply(self)

        self.initLayout()
        self.connectSignalToSlot()

    def initLayout(self):
        self.settingLabel.move(36, 30)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)

        self.preferencesGroup.addSettingCard(self.minimizeAsTray)
        self.preferencesGroup.addSettingCard(self.showOnStartup)
        self.preferencesGroup.addSettingCard(self.startWithWindows)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.preferencesGroup)


    def connectSignalToSlot(self):

        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))