import sys

from PyQt6 import QtWidgets
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import QMessageBox

from components.MainWindow import Ui_MainWindow
from utilities import make_window_center


# Create the connection
def createConnection():
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("./database/nea.db")
    if not con.open():
        QMessageBox.critical(
            None,
            "NEA Application - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    if not createConnection():
        sys.exit(1)
    window = MainWindow()
    """ Make Window center of screen """
    make_window_center(window)
    window.show()
    app.exec()
