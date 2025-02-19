import ctypes
from PyQt6.QtWidgets import QLineEdit, QMessageBox


def show_console():
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 4)

def hide_console():
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def show_dialog_ok(title, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()

def show_dialog_y_n(title, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Question)
        ret = msgBox.question(msgBox, title, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No )
        if ret == QMessageBox.StandardButton.Yes:
                return True
        return False
                