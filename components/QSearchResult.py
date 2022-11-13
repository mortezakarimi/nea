# Form implementation generated from reading ui file 'QSearchResult.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtWidgets import QWidget, QHeaderView, QSizePolicy

from Models.ProductModel import ProductModel
from utilities import make_window_center


class _Ui_SearchResult(object):
    AUTO = "Auto"
    LOWEST_PRICE = "Lowest Price"
    HIGHEST_RATING = "Highest Rating"
    BEST_DEAL = "Best Deal"
    FILTER_ITEMS = [AUTO,
                    LOWEST_PRICE,
                    HIGHEST_RATING,
                    BEST_DEAL]

    def __init__(self):
        print(self.FILTER_ITEMS)
        self.filterComboBox: QtWidgets.QComboBox | None = None
        self.tableView: QtWidgets.QTableView | None = None

    def setupUi(self, SearchResult):
        SearchResult.setObjectName("search_result")
        SearchResult.resize(800, 600)
        self.container = QtWidgets.QHBoxLayout()
        self.container.setContentsMargins(0, 0, 0, 0)
        SearchResult.setLayout(self.container)

        self.vcontainer = QtWidgets.QVBoxLayout()
        self.vcontainer.setContentsMargins(0, 0, 0, 0)

        self.filterHLayout = QtWidgets.QHBoxLayout()
        self.filterHLayout.setContentsMargins(0, 0, 0, 0)
        self.filterHLayout.setSpacing(0)
        self.filterHLayout.setObjectName("filterHLayout")

        self.filterLabel = QtWidgets.QLabel(SearchResult)
        self.filterLabel.setObjectName("filterLabel")
        self.filterLabel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.filterHLayout.addWidget(self.filterLabel)

        self.filterComboBox = QtWidgets.QComboBox(SearchResult)
        self.filterComboBox.setObjectName("filterComboBox")
        self.filterComboBox.setContentsMargins(0, 0, 0, 0)
        self.filterComboBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)

        self.filterComboBox.addItems(self.FILTER_ITEMS)
        self.filterComboBox.currentTextChanged.connect(self.onChanged)

        self.filterHLayout.addWidget(self.filterComboBox)
        self.vcontainer.addLayout(self.filterHLayout)

        self.tableView = QtWidgets.QTableView(SearchResult)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.setContentsMargins(0, 0, 0, 0)
        self.tableView.setSortingEnabled(True)
        self.tableView.resizeColumnsToContents()
        self.tableView.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.vcontainer.addWidget(self.tableView)
        self.container.addLayout(self.vcontainer)
        self.retranslateUi(SearchResult)
        QtCore.QMetaObject.connectSlotsByName(SearchResult)
        make_window_center(SearchResult)

    def retranslateUi(self, SearchResult):
        _translate = QtCore.QCoreApplication.translate

        self.filterLabel.setText(_translate("Result Filter", "Result Filter"))
        SearchResult.setWindowTitle(_translate("Search Result", "Search Result"))


class QSearchResult(QWidget, _Ui_SearchResult):
    def __init__(self, *args, obj=None, **kwargs):
        super(QSearchResult, self).__init__()
        self.setupUi(self)

        if 'model' in kwargs:
            self.tableView.setModel(kwargs['model'])

    def setModel(self, model):
        self.tableView.setModel(model)

    def onChanged(self, text):
        model = ProductModel()
        match text:
            case self.AUTO:
                pass
            case self.LOWEST_PRICE:
                model.asLowestPrice()
            case self.HIGHEST_RATING:
                model.asHighestRating()
            case self.BEST_DEAL:
                model.asBestDeal()
            case _:
                pass
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        self.setModel(proxy)