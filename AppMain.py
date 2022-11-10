from PyQt6.QtCore import QThreadPool, pyqtSignal, pyqtSlot, QMutex
from PyQt6.QtWidgets import QMessageBox, QWidget

import common
from Workers.Worker import Worker
from main import Main


class AppMain(QWidget, Main):
    search_term: str | None

    logMessage = pyqtSignal(str)
    logProduct = pyqtSignal(object)

    def __init__(self, window: QWidget):
        super().__init__()
        self.mutex = QMutex()
        self.progress = None
        self.window = window
        self.search_term = None

        self.logProduct.connect(lambda x: self._products.append(x))

    def set_search_term(self, search_term):
        self.search_term = search_term

    def _find_in_database(self):
        db = self._init_db_connection()
        keyword_result = db.find_search_term(self.search_term)
        if keyword_result is not None:
            button = QMessageBox.question(self.window, "Reload Result confirmation",
                                          "This search term already exist and saved on \"{0}\", Do you want to reload "
                                          "search from database?".format(keyword_result['search_date']))
            return button == QMessageBox.StandardButton.Yes

    def _save_into_database(self):
        button = QMessageBox.question(self.window, "Operation Completed", "Do you want save result into database?")
        if button == QMessageBox.StandardButton.Yes:
            db = self._init_db_connection()
            db.save_search_term(self.search_term)
            db.save_products(self.search_term, self._products)
            db.commit()

    @pyqtSlot(object)
    def set_product_data(self, product):
        self.logMessage.emit("\"{}\" processed.".format(product['title']))
        self.logProduct.emit(product)

    def start(self, force_fetch: bool = False):

        if not self._find_in_database():
            self.logMessage.emit("Start searching...")
            self._amazon_URL = common.create_amazon_url(self.search_term)
            page = common.load_url(self._amazon_URL)
            self.logMessage.emit("Search result page downloaded completely")
            search_results = self._calculate_page_results(page)
            self.logMessage.emit("Start Processing products")
            for res in search_results:
                processProductInformation = Worker(common.extract_link_and_rating_info, res)
                processProductInformation.setAutoDelete(False)
                processProductInformation.signals.result.connect(self.set_product_data)

                QThreadPool.globalInstance().start(processProductInformation)

            self.logMessage.emit("Start Processing products fakespot data")
            self._process_fake_spot_information()

            self.logMessage.emit("Start Processing products camelcamelcamel data")
            self._process_camelcamelcamel_information()

            self._save_into_database()
