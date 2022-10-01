import concurrent.futures
import json
import multiprocessing
import queue
import re
import threading
import time
import urllib.parse

# noinspection PyUnresolvedReferences
import cchardet  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
# noinspection PyUnresolvedReferences
import lxml  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
from progress.bar import Bar

import common
import fakespot_api

exitFlag = 0


def create_amazon_url():
    amazon_URL = 'https://www.amazon.co.uk/s?'
    search_query = input("What product do you want to search for?")
    amazon_params = {"k": search_query}
    amazon_URL += urllib.parse.urlencode(amazon_params)
    return amazon_URL


amazon_URL = create_amazon_url()
products = []
links = []


def extract_link_and_rating_info(product_html):
    product = {"rating": {'num_stars': 0.0, 'num_ratings': 0}, "link": ""}
    span_rating = product_html.find("span", {"aria-label": re.compile("out of 5 stars$")})
    if span_rating:
        product['asin'] = product_html['data-asin']
        product['rating']['num_stars'] = float(span_rating["aria-label"][:3])
        product['rating']['num_ratings'] = int(span_rating.find_next_sibling()["aria-label"].replace(",", ""))
        product['price'] = product_html.find('span', attrs={"class": "a-price"}).find('span').text[1:]
        product['link'] = 'https://www.amazon.co.uk/dp/{asin}/'.format(asin=product['asin'])

    return product


class ThreadHandler(threading.Thread):
    def __init__(self, thread_id, q):
        threading.Thread.__init__(self)
        self.thread_id = str(thread_id)
        self.q = q

    def run(self):
        # print("Starting Process-" + self.thread_id)
        process_data(self.q)
        # print("Exiting  Process-" + self.thread_id)


def process_data(q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            prod = extract_link_and_rating_info(data)
            products.append(prod)
            bar.next()
            queueLock.release()
        else:
            queueLock.release()
            time.sleep(1)


print("Loading search page...")
page = common.load_url(amazon_URL)
print("Calculate page data...")
soup = common.make_soup(page)

search_results = soup.find_all(attrs={"data-component-type": "s-search-result"})

total_search_results = len(search_results)

queueLock = threading.Lock()
workQueue = queue.Queue(total_search_results)
threads = []

print("Processing {total} product(s) information\n".format(total=total_search_results))

bar = Bar('Processing', max=total_search_results)

# Create new threads
for threadID in range(multiprocessing.cpu_count()):
    thread = ThreadHandler(threadID, workQueue)
    thread.start()
    threads.append(thread)

# Fill the queue
queueLock.acquire()
for result in search_results:
    workQueue.put(result)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1
# Wait for all threads to complete
for t in threads:
    t.join()

print("\nProcessing fake spot data")

fakeSpots = fakespot_api.FakeSpot.get_asins_bulk([item["asin"] for item in products if item["asin"] is not None])

with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    for index, value in enumerate(products):
        if value["asin"] in fakeSpots:
            if len(fakeSpots[value["asin"]]) < 3:
                [grade, rate] = fakeSpots[value["asin"]]
                isOutdated = True
            else:
                [grade, rate, isOutdated, _] = fakeSpots[value["asin"]]

            if isOutdated:
                th = executor.submit(fakespot_api.FakeSpot.analyse_product,
                                     value["link"])
                [grade, rate] = th.result()

            value["fake_spot"] = [
                grade,
                rate
            ]
            products[index] = value
        else:
            value["fake_spot"] = [
                "?",
                None
            ]

print(json.dumps(products, indent=4, default=str))
