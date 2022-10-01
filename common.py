import ssl
from urllib.request import urlopen, Request

# noinspection PyUnresolvedReferences
import cchardet  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
import certifi
# noinspection PyUnresolvedReferences
import lxml  # https://beautiful-soup-4.readthedocs.io/en/latest/#improving-performance
from bs4 import BeautifulSoup


def load_url(url):
    headers = {
        "Accept": "text/html",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Dnt": "1",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    context = ssl.create_default_context(cafile=certifi.where())
    req = urlopen(Request(url, headers=headers), context=context)
    return req


def make_soup(page):
    html = page.read()
    soup = BeautifulSoup(html, "lxml")
    return soup
