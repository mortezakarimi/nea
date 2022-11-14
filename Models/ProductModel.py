import typing

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColorConstants
from PyQt6.QtSql import QSqlQuery, QSqlQueryModel


class ProductModel(QSqlQueryModel):
    DEFAULT_QUERY = '''
        SELECT st.keyword,
       product."id",
       product."title",
       product."price",
       product."highest_price",
       product."lowest_price",
       product."link",
       product."amazon_rating_stars",
       product."amazon_rating_total",
       product."fake_spot_grade",
       product."fake_spot_rating",
       CASE
           WHEN product.highest_price + product.lowest_price == 0 THEN null
           ELSE (((product.highest_price + product.lowest_price) / 2) - product.price) /
                      (product.highest_price + product.lowest_price) * 100 END as deal
FROM product
     LEFT JOIN search_term_product stp on product.id = stp.product_id
     LEFT JOIN search_term st on stp.search_keyword = st.keyword'''

    def __init__(self, *args, **kwargs):
        super(ProductModel, self).__init__(*args, **kwargs)
        self.colorize = False
        self.default_query = QSqlQuery()
        self.default_query.prepare(self.DEFAULT_QUERY)
        self.default_query.exec()
        self.setQuery(self.default_query)
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Search Term")
        self.setHeaderData(1, Qt.Orientation.Horizontal, "ID")
        self.setHeaderData(2, Qt.Orientation.Horizontal, "Title")
        self.setHeaderData(3, Qt.Orientation.Horizontal, "Price")
        self.setHeaderData(4, Qt.Orientation.Horizontal, "Highest Price")
        self.setHeaderData(5, Qt.Orientation.Horizontal, "Lowest Price")
        self.setHeaderData(6, Qt.Orientation.Horizontal, "Link")
        self.setHeaderData(7, Qt.Orientation.Horizontal, "Amazon Rating Stars")
        self.setHeaderData(8, Qt.Orientation.Horizontal, "Amazon Rating Total")
        self.setHeaderData(9, Qt.Orientation.Horizontal, "Fake Spot Grade")
        self.setHeaderData(10, Qt.Orientation.Horizontal, "Fake Spot Rating")
        self.setHeaderData(11, Qt.Orientation.Horizontal, "Deal")

    def flags(self, index: QtCore.QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled

    def asLowestPrice(self):
        self.colorize = True
        self.default_query.prepare('''
        SELECT st.keyword,
       product."id",
       product."title",
       product."price",
       product."highest_price",
       product."lowest_price",
       product."link",
       product."amazon_rating_stars",
       product."amazon_rating_total",
       product."fake_spot_grade",
       product."fake_spot_rating",
       CASE
           WHEN product.highest_price + product.lowest_price == 0 THEN null
           ELSE (((product.highest_price + product.lowest_price) / 2) - product.price) /
                      (product.highest_price + product.lowest_price) * 100 END as deal
FROM product
     LEFT JOIN search_term_product stp on product.id = stp.product_id
     LEFT JOIN search_term st on stp.search_keyword = st.keyword
     WHERE product.price <> 0 ORDER BY price''')
        self.default_query.exec()
        self.setQuery(self.default_query)

    def asHighestRating(self):
        self.colorize = True
        self.default_query.prepare('''
                SELECT st.keyword,
               product."id",
               product."title",
               product."price",
               product."highest_price",
               product."lowest_price",
               product."link",
               product."amazon_rating_stars",
               product."amazon_rating_total",
               product."fake_spot_grade",
               product."fake_spot_rating",
               CASE
           WHEN product.highest_price + product.lowest_price == 0 THEN null
           ELSE (((product.highest_price + product.lowest_price) / 2) - product.price) /
                      (product.highest_price + product.lowest_price) * 100 END as deal
        FROM product
             LEFT JOIN search_term_product stp on product.id = stp.product_id
             LEFT JOIN search_term st on stp.search_keyword = st.keyword
             WHERE product.price <> 0 ORDER BY product.fake_spot_grade ,product.fake_spot_rating DESC''')
        self.default_query.exec()
        self.removeColumn(11)
        self.setQuery(self.default_query)

    def asBestDeal(self):
        self.colorize = True
        self.default_query.prepare('''
                SELECT st.keyword,
       product."id",
       product."title",
       product."price",
       product."highest_price",
       product."lowest_price",
       product."link",
       product."amazon_rating_stars",
       product."amazon_rating_total",
       product."fake_spot_grade",
       product."fake_spot_rating",
       CASE
           WHEN product.highest_price + product.lowest_price == 0 THEN null
           ELSE (((product.highest_price + product.lowest_price) / 2) - product.price) /
                      (product.highest_price + product.lowest_price) * 100 END as deal
FROM product
         LEFT JOIN search_term_product stp on product.id = stp.product_id
         LEFT JOIN search_term st on stp.search_keyword = st.keyword
WHERE product.price <> 0
ORDER BY deal DESC''')
        self.default_query.exec()
        self.removeColumn(11)
        self.setQuery(self.default_query)

    def data(self, item: QtCore.QModelIndex, role: int = ...) -> typing.Any:
        if not item.isValid():
            return QSqlQueryModel.data(self, item, role)
            # vvvv this is the magic part
        elif role == Qt.ItemDataRole.BackgroundRole and self.colorize:
            match item.row():
                case 0:
                    return QBrush(QColorConstants.Svg.green)

                case 1:
                    return QBrush(QColorConstants.Svg.forestgreen)

                case 2:
                    return QBrush(QColorConstants.Svg.limegreen)

        if role == Qt.ItemDataRole.DisplayRole and item.column() == 11:
            deal = QSqlQueryModel.data(self, item, role)
            if deal != "":
                deal = round(deal,2)
                print(deal)
                return f"{deal}%"
            return deal

        # ^^^^ this is the magic part
        return QSqlQueryModel.data(self, item, role)
