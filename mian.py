from PyQt6.QtWidgets import QApplication
from classes import Uitgooi
import sys
from shared.paths import STYLE
from qt_material import apply_stylesheet

def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_amber.xml')

    ug = Uitgooi()
    ug.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()