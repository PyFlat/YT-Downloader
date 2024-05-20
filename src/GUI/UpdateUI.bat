cd Interfaces
pyside6-uic MainInterface.ui -o MainInterface_ui.py
py ../PyFromUi.py MainInterface_ui.py MainInterface.py QWidget

pyside6-uic DownloadInterface.ui -o DownloadInterface_ui.py
py ../PyFromUi.py DownloadInterface_ui.py DownloadInterface.py QWidget

cd ..
cd CustomWidgets

pyside6-uic InformationWidget.ui -o InformationWidget_ui.py
py ../PyFromUi.py InformationWidget_ui.py InformationWidget.py QWidget

pyside6-uic DownloadWidget.ui -o DownloadWidget_ui.py
py ../PyFromUi.py DownloadWidget_ui.py DownloadWidget.py QFrame