import sys
from PyQt6.QtWidgets import QApplication
from arayuz.ana_pencere import MediaStaffApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MediaStaffApp()
    window.show()
    sys.exit(app.exec())