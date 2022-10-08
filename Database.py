import os.path
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: str):
        """ create a database connection to a SQLite database """
        directory_path = Path(os.path.dirname(path))
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def initialize_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_term
            (
                keyword     text primary key,
                result_rank integer default -1,
                search_date text not null
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product
            (
                id                      text primary key,
                title                   text    null ,
                price                   real null ,
                link                    text null ,
                amazon_rating_stars     real    null ,
                amazon_rating_total     real    null ,
                fake_spot_grade         text    null ,
                fake_spot_rating        real    null ,
                highest_price           integer null,
                lowest_price            integer null
            );
                """)
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_term_product
                (
                    search_keyword text not null,
                    product_id     text not null,
                    FOREIGN KEY (search_keyword) REFERENCES search_term (keyword),
                    FOREIGN KEY (product_id) REFERENCES product (id)
                )
                """)

    def save_search_term(self, term: str, rank: int = -1) -> str:
        self.cursor.execute("INSERT INTO search_term VALUES (?,?,datetime('now'))", [term, rank])
        return self.cursor.lastrowid

    def save_products(self, term: str, products: []):
        for product in products:
            self.cursor.execute(
                """
                INSERT INTO product (id, title, price, link, amazon_rating_stars, amazon_rating_total, fake_spot_grade, fake_spot_rating, highest_price, lowest_price)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                [product['asin'], product['title'], product['link'], product['price'], product['rating']['num_stars'],
                 product['rating']['num_ratings'], product['fake_spot'][0], product['fake_spot'][1],
                 product['price'], product['price']])
            self.cursor.execute("INSERT INTO search_term_product (search_keyword, product_id) values (?,?)",
                                [term, product['asin']])

    def commit(self):
        self.connection.commit()

    def find_search_term(self, term):
        self.cursor.execute("SELECT * FROM search_term WHERE keyword = ?", [term])
        return self.cursor.fetchone()

    def retrieve_products(self, term):
        self.cursor.execute(
            "SELECT * FROM product INNER JOIN search_term_product stp on product.id = stp.product_id WHERE "
            "stp.search_keyword = ?",
            [term])
        rows = self.cursor.fetchall()
        products = []
        for row in rows:
            products.append({
                "asin": row['id'],
                "title": row['title'],
                "price": row['price'],
                "link": row['link'],
                "rating": {"num_stars": row['amazon_rating_stars'], "num_ratings": row['amazon_rating_total']},
                "fake_spot": [row['fake_spot_grade'], row['fake_spot_rating']],
                "highest_price": row['highest_price'],
                "lowest_price": row['lowest_price']
            })

        return products
