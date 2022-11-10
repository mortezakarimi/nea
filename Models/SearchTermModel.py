from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlRelationalTableModel


class SearchTermModel(QSqlRelationalTableModel):
    def __init__(self, *args, **kwargs):
        super(SearchTermModel, self).__init__(*args, **kwargs)
        self.setTable("search_term")
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Keyword")
        self.setHeaderData(1, Qt.Orientation.Horizontal, "Result Rank")
        self.setHeaderData(2, Qt.Orientation.Horizontal, "Search Date")
        self.sort(2, Qt.SortOrder.DescendingOrder)
