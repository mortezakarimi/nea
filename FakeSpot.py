import json
import re
import urllib.parse

import requests
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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
            "asins": json.dumps(asins_list, separators=(',', ':')),
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

    @staticmethod
    def analyse_product(url):
        print("Analyse product with \"{link}\" Is Outdated".format(link=url))
        fakespot_url = "https://www.fakespot.com/analyze?"
        params = urllib.parse.urlencode({
            "url": url,
            "ra": "true"
        })

        # Create a request interceptor
        def interceptor(request):
            del request.headers['Referer']  # Delete the header first
            request.headers['Referer'] = 'https://www.google.com/'
            request.headers['Accept'] = 'text/html'
            request.headers['Dnt'] = '1'
            request.headers['Upgrade-Insecure-Requests'] = '1'
            request.headers[
                'User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
            # request.headers[f"{csrf_param}"] = csrf_token

        options = Options()
        # options.experimental_options['detach'] = True
        options.add_argument("--window-size=1920,1080")
        # options.headless = True
        options.add_argument(
            f'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36')
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.request_interceptor = interceptor
        driver.get(fakespot_url + params)
        try:
            elm = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                  '.button_to .blue-button, '
                                                                                  '.analysis-status')))
            if elm.tag_name == 'button':
                elm.submit()
                WebDriverWait(driver, 300).until_not(lambda x: x.find_element(By.CSS_SELECTOR, '.popup-box'))

            elif elm.tag_name == 'div':
                WebDriverWait(driver, 300).until_not(lambda x: x.find_element(By.CSS_SELECTOR, '.popup-box'))

        except TimeoutException as e:
            print("Product already updated.")

        finally:
            try:
                grade_value = driver.find_element(By.CSS_SELECTOR, '.review-grade .grade-box p')
                grade = grade_value.get_attribute("innerHTML")
            except NoSuchElementException as e:
                grade = "?"
            try:
                rating_value = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="ratingValue"]')
                rating = rating_value.get_attribute("innerHTML")
            except NoSuchElementException as e:
                rating = None

            return grade, rating
