import argparse
import concurrent.futures
import json
import multiprocessing
import queue
import sys
import threading
import time
from decimal import Decimal

# noinspection PyUnresolvedReferences
import cchardet  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
# noinspection PyUnresolvedReferences
import lxml  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
from progress.bar import Bar

import common
from Camelize import Camelize
from Database import Database
from FakeSpot import FakeSpot
from ThreadHandler import ThreadHandler
from common import create_amazon_url, extract_link_and_rating_info, confirm


class Main:
    def __init__(self, search_term: str = None):
        self.search_term = search_term
        self._total_search_results = None
        self._bar = None
        self._queueLock = threading.Lock()
        self._workQueue = None
        self._exitFlag = 0
        self._amazon_URL = None
        self._products = []
        self._links = []

    def _process_data(self, q):
        while not self._exitFlag:
            self._queueLock.acquire()
            if not self._workQueue.empty():
                data = q.get()
                prod = extract_link_and_rating_info(data)
                if prod:
                    self._products.append(prod)

                self._bar.next()
                self._queueLock.release()
            else:
                self._queueLock.release()
                time.sleep(1)

    def _process_fake_spot_information(self):
        common.print_console("\nProcessing fake spot data")
        fake_spots = FakeSpot.get_asins_bulk(
            [item["asin"] for item in self._products])
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            for index, value in enumerate(self._products):
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
                    self._products[index] = value
                else:
                    value["fake_spot"] = [
                        "?",
                        None
                    ]

    def _process_camelcamelcamel_information(self):
        common.print_console("\nProcessing CamelCamelCamel data")
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            for index, value in enumerate(self._products):
                c = Camelize(value['asin'])
                camel_result = c.get()
                if common.keys_exists(camel_result, 'highest_pricing', 'price_amazon', 'price'):
                    value["highest_price"] = str(Decimal(
                        camel_result['highest_pricing']['price_amazon']['price']) / Decimal(
                        100))
                else:
                    value["highest_price"] = str(Decimal(0))
                if common.keys_exists(camel_result, 'lowest_pricing', 'price_amazon', 'price'):
                    value["lowest_price"] = str(
                        Decimal(camel_result['lowest_pricing']['price_amazon']['price']) / Decimal(
                            100))
                else:
                    value["lowest_price"] = str(Decimal(0))

                self._products[index] = value

    def _process_product_information(self, search_results):
        self._workQueue = queue.Queue(self._total_search_results)
        threads = []
        common.print_console("Processing {total} product(s) information\n".format(total=self._total_search_results))
        sys.stdout.flush()
        sys.stderr.flush()
        self._bar = Bar('Processing', max=self._total_search_results)
        # Create new threads
        for threadID in range(multiprocessing.cpu_count()):
            thread = ThreadHandler(threadID, self._workQueue, self._process_data)
            thread.start()
            threads.append(thread)
        # Fill the queue
        self._queueLock.acquire()
        for result in search_results:
            self._workQueue.put(result)
        self._queueLock.release()
        # Wait for queue to empty
        while not self._workQueue.empty():
            pass
        # Notify threads it's time to exit
        self._exitFlag = 1
        # Wait for all threads to complete
        for t in threads:
            t.join()

    def _calculate_page_results(self, page):
        common.print_console("Calculate page data...")
        soup = common.make_soup(page)
        search_results = soup.find_all(attrs={"data-component-type": "s-search-result"})
        self._total_search_results = len(search_results)
        return search_results

    def _find_in_database(self):
        db = self._init_db_connection()
        keyword_result = db.find_search_term(self.search_term)
        if keyword_result is not None:
            if confirm("This search term already exist and saved on \"{0}\", Do you want to reload search from "
                       "database?".format(keyword_result['search_date'])):
                self._products = db.retrieve_products(self.search_term)
                self.print()

    def _save_into_database(self, force_save=False):
        if force_save or confirm("Do you want save result into database?"):
            db = self._init_db_connection()
            db.save_search_term(self.search_term)
            db.save_products(self.search_term, self._products)
            db.commit()

    @staticmethod
    def _init_db_connection():
        db = Database("./database/nea.db")
        db.initialize_tables()
        return db

    @staticmethod
    def _get_search_term():
        if len(sys.argv) > 1:
            common.print_console("Your selected search term: {0}".format(sys.argv[1]))
            return sys.argv[1]

        return input("What product do you want to search for?")

    def reset(self):
        self.search_term = None
        self._total_search_results = None
        self._bar = None
        self._queueLock = threading.Lock()
        self._workQueue = None
        self._exitFlag = 0
        self._amazon_URL = None
        self._products = []
        self._links = []

    def print(self):
        common.print_console(json.dumps(self._products, indent=4, default=str))

    def start(self, **kwargs):
        while True:
            self.search_term = self._get_search_term()
            if self.search_term.strip() != "":
                break

        if not kwargs['force_fetch']:
            self._find_in_database()

        if len(self._products) == 0:
            self._amazon_URL = create_amazon_url(self.search_term)
            common.print_console("Loading search page...")
            page = common.load_url(self._amazon_URL)
            search_results = self._calculate_page_results(page)

            self._process_product_information(search_results)

            # Make sure all products is unique
            self._products = list({v['asin']: v for v in self._products if v["asin"] is not None}.values())

            self._process_fake_spot_information()
            self._process_camelcamelcamel_information()

            if kwargs['print'] or confirm("Do you want to print result?"):
                self.print()

            self._save_into_database(kwargs['force_save'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='NEA', usage='%(prog)s [options]')
    parser.add_argument('search_term', nargs='?')
    parser.add_argument('-f', '--force-fetch',
                        help='Force application to request your search term from amazon, and skip checking already '
                             'exist search term in database',
                        action='store_true')
    parser.add_argument('-s', '--force-save',
                        help='Force application to save search term in database',
                        action='store_true')
    parser.add_argument('-p', '--print',
                        help='Print search result',
                        action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    app = Main(args.search_term)
    app.start(force_fetch=args.force_fetch, force_save=args.force_save, print=args.print)
