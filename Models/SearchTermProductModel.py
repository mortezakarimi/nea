from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlRelationalTableModel, QSqlRelation


class SearchTermProductModel(QSqlRelationalTableModel):
    def __init__(self, *args, **kwargs):
        super(SearchTermProductModel, self).__init__(*args, **kwargs)
        self.setTable("search_term_product")
        self.setRelation(0, QSqlRelation("search_term", "keyword", "keyword"))
        self.setRelation(1, QSqlRelation("product", "id", "name"))
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Search Term")
        self.setHeaderData(1, Qt.Orientation.Horizontal, "Product")
