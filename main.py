import json
import multiprocessing
import queue
import threading
import time
import urllib.parse

import common

exitFlag = 0


def create_amazon_url():
    amazon_URL = 'https://www.amazon.co.uk/s?'
    search_query = input("What product do you want to search for?")
    amazon_params = {"k": search_query}
    amazon_URL += urllib.parse.urlencode(amazon_params)
    return amazon_URL


amazon_URL = create_amazon_url()
products = []


def extract_link_and_rating_info(div):
    children = div.findChildren()
    product = {"rating": {'num_stars': 0.0, 'num_ratings': 0}, "link": ""}
    for rating_tag in children:
        if rating_tag.name == 'span' and rating_tag.has_attr('aria-label') and rating_tag['aria-label'].endswith(
                'out of 5 stars'):
            num_str = rating_tag['aria-label'][:3]
            product['rating']['num_stars'] = float(num_str)
        elif rating_tag.name == 'span' and rating_tag.has_attr('class') and ' '.join(
                rating_tag['class']) == 'a-size-base s-underline-text':
            product['rating']['num_ratings'] = int(rating_tag.text.replace(",", ""))
        elif rating_tag.name == 'a' and rating_tag.has_attr('class') and ' '.join(
                rating_tag['class']) == 'a-link-normal s-underline-text s-underline-link-text s-link-style':
            product['link'] = 'https://www.amazon.co.uk' + rating_tag['href']
    return product


class ThreadHandler(threading.Thread):
    def __init__(self, thread_id, q):
        threading.Thread.__init__(self)
        self.thread_id = str(thread_id)
        self.q = q

    def run(self):
        print("Starting Process-" + self.thread_id)
        process_data(self.q)
        print("Exiting  Process-" + self.thread_id)


def process_data(q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            rating_div = data.find("div", {"class": "a-row a-size-small"})
            price_span = data.find("span", {"class": "a-offscreen"})
            if (rating_div is None) or (price_span is None):
                pass
            else:
                prod = extract_link_and_rating_info(rating_div)
                products.append(prod)
                price = price_span.text
                prod["price"] = float(price[1:])
            queueLock.release()
        else:
            queueLock.release()
            time.sleep(1)


page = common.load_url(amazon_URL)
soup = common.make_soup(page)

search_results = soup.find_all("div", {"data-asin": True})

total_search_results = len(search_results)

queueLock = threading.Lock()
workQueue = queue.Queue(total_search_results)
threads = []

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

print(json.dumps(products, indent=4, default=str))
