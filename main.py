import sys
from logger import setup_logging
from config import settings
from gui import MainWindow
from gui_theme import GLOBAL_QSS
import os


if getattr(sys, 'stderr', None) is None:
    sys.stderr = open(os.devnull, 'w')

if getattr(sys, 'stdout', None) is None:
    sys.stdout = open(os.devnull, 'w')

from PySide6 import QtWidgets

if __name__ == "__main__":
    setup_logging(settings.log_level)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_QSS)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())