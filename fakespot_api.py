import json
import re

import requests


class FakeSpot:
    @staticmethod
    def get_asin(href):
        asin = re.search(r'/[d]p/([^/]+)', href, flags=re.IGNORECASE)
        if asin:
            return asin.group(1)
        return None

    @staticmethod
    def get_asins_bulk(asins_list):

        url = "https://trustwerty.com/api/bulk-asins"

        payload = {
            "asins": json.dumps(asins_list,separators=(',', ':')),
            "noCache": True,
            "tld": "co.uk",
            "user_id": "105036178713829078477"
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        return []

    @staticmethod
    def get_asin_info(asin):
        r = requests.post('https://trustwerty.com/api/highlights', json={
            'asin': asin,
            'noCache': True,
            "tld": "co.uk",
            "user_id": "105036178713829078477"
        })
        return r.json()

    @staticmethod
    def get_product_info(product):
        asin = FakeSpot.get_asin(product)
        return FakeSpot.get_asin_info([asin])

    @staticmethod
    def get_products_info(product_links):
        asins = []
        for product_links in product_links:
            asin = FakeSpot.get_asin(product_links)
            if asin:
                asins.append(asin)
        return FakeSpot.get_asins_bulk(asins)
