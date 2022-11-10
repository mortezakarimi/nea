from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlRelationalTableModel, QSqlRelation


class ProductModel(QSqlRelationalTableModel):
    def __init__(self, *args, **kwargs):
        super(ProductModel, self).__init__(*args, **kwargs)
        self.setTable("product")
        self.setJoinMode(self.JoinMode.LeftJoin)
        self.setRelation(0, QSqlRelation("search_term_product", "product_id", "search_keyword"))
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Search Term")
        self.setHeaderData(self.fieldIndex("id"), Qt.Orientation.Horizontal, "ID")
        self.setHeaderData(self.fieldIndex("title"), Qt.Orientation.Horizontal, "Title")
        self.setHeaderData(self.fieldIndex("link"), Qt.Orientation.Horizontal, "Link")
        self.setHeaderData(self.fieldIndex("price"), Qt.Orientation.Horizontal, "Price")
        self.setHeaderData(self.fieldIndex("amazon_rating_stars"), Qt.Orientation.Horizontal, "Amazon Rating Stars")
        self.setHeaderData(self.fieldIndex("amazon_rating_total"), Qt.Orientation.Horizontal, "Amazon Rating Total")
        self.setHeaderData(self.fieldIndex("fake_spot_grade"), Qt.Orientation.Horizontal, "Fake Spot Grade")
        self.setHeaderData(self.fieldIndex("fake_spot_rating"), Qt.Orientation.Horizontal, "Fake Spot Rating")
        self.setHeaderData(self.fieldIndex("highest_price"), Qt.Orientation.Horizontal, "Highest Price")
        self.setHeaderData(self.fieldIndex("lowest_price"), Qt.Orientation.Horizontal, "Lowest Price")
        self.sort(1, Qt.SortOrder.AscendingOrder)

    def flags(self, index: QtCore.QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled
