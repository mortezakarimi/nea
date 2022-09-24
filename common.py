import ssl
from urllib.request import urlopen, Request

# noinspection PyUnresolvedReferences
import cchardet  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
import certifi
# noinspection PyUnresolvedReferences
import lxml  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
from bs4 import BeautifulSoup


def load_url(url):
    # Request(url)
    # req.add_headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    context = ssl.create_default_context(cafile=certifi.where())
    req = urlopen(Request(url, headers=headers), context=context)
    return req


def make_soup(page):
    html = page.read()
    soup = BeautifulSoup(html, "lxml")
    return soup
