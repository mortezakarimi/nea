import json
import re

import requests


class FakeSpot:
    @staticmethod
    def get_asin(href):
        asin = re.search(r'/[dg]p/([^/]+)', href, flags=re.IGNORECASE)
        if asin:
            return asin.group(1)
        return None

    @staticmethod
    def get_asins_bulk(asins_list):
        r = requests.post('https://trustwerty.com/api/bulk-asins', data={
            'asins': json.dumps(asins_list),
            'noCache': True,
            "tld": "co.uk",
            "user_id": "105036178713829078477"
        })
        return r.json()

    @staticmethod
    def get_asin_info(asin):
        r = requests.post('https://trustwerty.com/api/highlights', data={
            'asin': asin,
            'noCache': True,
            "tld": "co.uk",
            "user_id": "105036178713829078477"
        })
        return r.json()

    @staticmethod
    def get_product_info(product):
        asin = FakeSpot.get_asin(product)
        return FakeSpot.get_asin_info(asin)

    @staticmethod
    def get_products_info(product_links):
        asins = []
        for product_links in product_links:
            asins.append(FakeSpot.get_asin(product_links))
        return FakeSpot.get_asin_info(asins)
