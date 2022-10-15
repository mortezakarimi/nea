from collections import namedtuple
from urllib.parse import urlencode, urlunparse

from zenrows import ZenRowsClient


class Camelize:
    _CAMELIZE_BASE_URL = 'izer.camelcamelcamel.com'
    _AMAZON_PRODUCT_ADDRESS = 'https://www.amazon.co.uk/dp/{asin}/'

    def __init__(self, amazon_asin: str):
        self._url = self._create_url(amazon_asin)

    def _create_url(self, amazon_asin, locale: str = 'UK'):
        # namedtuple to match the internal signature of urlunparse
        Components = namedtuple(
            typename='Components',
            field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
        )

        query_params = {
            'locale': locale.upper(),
            'ver': 5,
            'url': self._AMAZON_PRODUCT_ADDRESS.format(asin=amazon_asin)
        }
        url = urlunparse(
            Components(
                scheme='https',
                netloc=self._CAMELIZE_BASE_URL,
                query=urlencode(query_params),
                path='',
                url='/chromelizer/{asin}'.format(asin=amazon_asin),
                fragment=''
            )
        )
        return url

    @staticmethod
    def _fetch(url) -> dict:
        # Use proxy to bypass rate limit, See https://app.zenrows.com/
        client = ZenRowsClient("9546b9d7e8016593565d1231cb0dbd1de828054b")

        response = client.get(url)

        return response.json()

    def get(self):
        return self._fetch(self._url)
