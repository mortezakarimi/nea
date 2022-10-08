import re
import ssl
import urllib.parse
from urllib.request import urlopen, Request

import bs4
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


def create_amazon_url(search_term):
    amazon_url = 'https://www.amazon.co.uk/s?'
    amazon_params = {"k": search_term}
    amazon_url += urllib.parse.urlencode(amazon_params)
    return amazon_url


def extract_link_and_rating_info(product_html: bs4.element.Tag | bs4.element.NavigableString):
    product = {"rating": {'num_stars': 0.0, 'num_ratings': 0}, "link": "",
               'title': product_html.find('h2').text}
    span_rating = product_html.find("span", {"aria-label": re.compile("out of 5 stars$")})

    if product_html['data-asin']:
        product['asin'] = product_html['data-asin']
    else:
        return None

    if span_rating:
        product['rating']['num_stars'] = float(span_rating["aria-label"][:3])
        product['rating']['num_ratings'] = int(span_rating.find_next_sibling()["aria-label"].replace(",", ""))
        product['price'] = product_html.find('span', attrs={"class": "a-price"}).find('span').text[1:]
        product['link'] = 'https://www.amazon.co.uk/dp/{asin}/'.format(asin=product['asin'])

    return product


def confirm(question: str) -> bool:
    c = input("{0} [Y]Yes or [N]No:\n".format(question))
    if c.lower() != 'y' and c.lower() != 'n':
        print("\n Invalid Option. Please Enter a Valid Option.")
        return confirm(question)
    return c.lower() == 'y'
