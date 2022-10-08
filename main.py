import concurrent.futures
import json
import multiprocessing
import queue
import sys
import threading
import time

# noinspection PyUnresolvedReferences
import cchardet  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
# noinspection PyUnresolvedReferences
import lxml  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
from progress.bar import Bar

import common
from Database import Database
from FakeSpot import FakeSpot
from ThreadHandler import ThreadHandler
from common import create_amazon_url, extract_link_and_rating_info, confirm


class Main:
    def __init__(self):
        self.search_term = None
        self.__total_search_results = None
        self.__bar = None
        self.__queueLock = threading.Lock()
        self.__workQueue = None
        self.__exitFlag = 0
        self.__amazon_URL = None
        self.__products = []
        self.__links = []

    def __process_data(self, q):
        while not self.__exitFlag:
            self.__queueLock.acquire()
            if not self.__workQueue.empty():
                data = q.get()
                prod = extract_link_and_rating_info(data)
                if prod:
                    self.__products.append(prod)

                self.__bar.next()
                self.__queueLock.release()
            else:
                self.__queueLock.release()
                time.sleep(1)

    def __process_fake_spot_information(self):
        print("\nProcessing fake spot data")
        fake_spots = FakeSpot.get_asins_bulk(
            [item["asin"] for item in self.__products])
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            for index, value in enumerate(self.__products):
                if value["asin"] in fake_spots:
                    if len(fake_spots[value["asin"]]) < 3:
                        [grade, rate] = fake_spots[value["asin"]]
                        is_outdated = True
                    else:
                        [grade, rate, is_outdated, _] = fake_spots[value["asin"]]

                    if is_outdated:
                        th = executor.submit(FakeSpot.analyse_product,
                                             value["link"])
                        [grade, rate] = th.result()

                    value["fake_spot"] = [
                        grade,
                        rate
                    ]
                    self.__products[index] = value
                else:
                    value["fake_spot"] = [
                        "?",
                        None
                    ]

    def __process_product_information(self, search_results):
        self.__workQueue = queue.Queue(self.__total_search_results)
        threads = []
        print("Processing {total} product(s) information\n".format(total=self.__total_search_results))
        self.__bar = Bar('Processing', max=self.__total_search_results)
        # Create new threads
        for threadID in range(multiprocessing.cpu_count()):
            thread = ThreadHandler(threadID, self.__workQueue, self.__process_data)
            thread.start()
            threads.append(thread)
        # Fill the queue
        self.__queueLock.acquire()
        for result in search_results:
            self.__workQueue.put(result)
        self.__queueLock.release()
        # Wait for queue to empty
        while not self.__workQueue.empty():
            pass
        # Notify threads it's time to exit
        self.__exitFlag = 1
        # Wait for all threads to complete
        for t in threads:
            t.join()

    def __calculate_page_results(self, page):
        print("Calculate page data...")
        soup = common.make_soup(page)
        search_results = soup.find_all(attrs={"data-component-type": "s-search-result"})
        self.__total_search_results = len(search_results)
        return search_results

    def __find_in_database(self):
        db = self.__init_db_connection()
        keyword_result = db.find_search_term(self.search_term)
        if keyword_result is not None:
            if confirm("This search term already exist and saved on \"{0}\", Do you want to reload search from "
                       "database?".format(keyword_result['search_date'])):
                self.__products = db.retrieve_products(self.search_term)

    def __save_into_database(self):
        if confirm("Do you want save result into database?"):
            db = self.__init_db_connection()
            db.save_search_term(self.search_term)
            db.save_products(self.search_term, self.__products)
            db.commit()

    @staticmethod
    def __init_db_connection():
        db = Database("./database/nea.db")
        db.initialize_tables()
        return db

    @staticmethod
    def __get_search_term():
        if len(sys.argv) > 1:
            print("Your selected search term: {0}".format(sys.argv[1]))
            return sys.argv[1]

        return input("What product do you want to search for?")

    def reset(self):
        self.search_term = None
        self.__total_search_results = None
        self.__bar = None
        self.__queueLock = threading.Lock()
        self.__workQueue = None
        self.__exitFlag = 0
        self.__amazon_URL = None
        self.__products = []
        self.__links = []

    def print(self):
        print(json.dumps(self.__products, indent=4, default=str))

    def start(self):
        self.search_term = self.__get_search_term()
        self.__find_in_database()
        if len(self.__products) == 0:
            self.__amazon_URL = create_amazon_url(self.search_term)
            print("Loading search page...")
            page = common.load_url(self.__amazon_URL)
            search_results = self.__calculate_page_results(page)

            self.__process_product_information(search_results)

            # Make sure all products is unique
            self.__products = list({v['asin']: v for v in self.__products if v["asin"] is not None}.values())

            self.__process_fake_spot_information()

            self.__save_into_database()

        if confirm("Do you want to print result?"):
            self.print()


if __name__ == '__main__':
    app = Main()
    app.start()
