from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QApplication


def make_window_center(window):
    windowWidth = window.geometry().width()
    windowHeight = window.geometry().height()
    desktopWidth = QApplication.primaryScreen().geometry().width()
    desktopHeight = QApplication.primaryScreen().geometry().height()
    window.move(QPoint(int(desktopWidth / 2 - windowWidth / 2), int(desktopHeight / 2 - windowHeight / 2)))

