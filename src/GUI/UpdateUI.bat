cd Interfaces
pyside6-uic MainInterface.ui -o MainInterface_ui.py
py ../PyFromUi.py MainInterface_ui.py MainInterface.py

cd ..
cd CustomWidgets

pyside6-uic InformationWidget.ui -o InformationWidget_ui.py
py ../PyFromUi.py InformationWidget_ui.py InformationWidget.py