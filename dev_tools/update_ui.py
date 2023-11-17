main_win  = open("ui_mainwindow.py", "r").read()
new = main_win[main_win.find("self.centralwidget = "):]


main_win_new = open("src/Ui_MainWindow.py", "r+").read()
old = main_win_new[:main_win_new.find("self.centralwidget")]
open("src/Ui_MainWindow.py", "w").write(old+new)
