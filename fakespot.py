import time
import threading

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


class fakespot(threading.Thread):
    def __init__(self, product):
        threading.Thread.__init__(self)
        self.product = product

    def run(self):
        openFakespotTab(self.product)


products = [
    'https://www.amazon.co.uk/SmithPackaging-Double-Cardboard-Moving-Handles/dp/B083NMTVS5/ref=sr_1_5?crid=1WRZDGDIAJ88R&keywords=box&qid=1661972994&sprefix=box%2Caps%2C124&sr=8-5',
    'https://www.amazon.co.uk/Levington-Tomorite-Liquid-Tomato-Concentrate/dp/B09RK3HPH5',
]

tabs = []


def extract_up_to_date_score(driver, just_analysed):
    print("entered extract")
    if just_analysed:
        xpath = '/html/body/div[7]/div/div[2]/div/div/div/div[2]/div/div[2]/div/div/p'
    else:
        xpath = '/html/body/div[6]/div/div[2]/div/div/div/div[2]/div/div[2]/div/div/p'
    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
    wrapper = driver.find_element(by=By.XPATH,value=xpath)
    return wrapper.text


def openFakespotTab(product):
    print("product", product)
    if product == 'https://www.amazon.co.uk/Batman-Court-Owls-Comics-Paperback/dp/1401235425/ref=sr_1_1?crid=1OFGTZ8WWQU08&keywords=batman+court+of+owls&qid=1660331429&sprefix=batman+court+%2Caps%2C63&sr=8-1':
        print("here")
    else:
        print("mismatch")
    user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
    options = Options()
    # options.experimental_options['detach'] = True
    options.add_argument("--window-size=1920,1080")
    # options.headless = True
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://www.fakespot.com/analyzer')
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#url-input-home"))).click()
    inputElement = driver.find_element(by=By.ID, value="url-input-home")
    inputElement.send_keys(product)
    time.sleep(1)
    inputElement.send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".reanalyze-message")))
        outdated = True
        print("Outdated")
    except:
        outdated = False
        print("Not outdated")
    # driver.get_screenshot_as_file("screenshot" + str(product[-1]) + ".png")
    if outdated:
        driver.find_element(by=By.CLASS_NAME, value='blue-button').click()
        print("Re-analyzing...")
        time.sleep(2)
        popup_running = True
        while popup_running:
            print("sleeping for 20 seconds")
            time.sleep(20)
            if len(driver.find_elements(By.CSS_SELECTOR, ".popup-box")) == 0:
                popup_running = False

        # WebDriverWait(driver, 120).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".popup-box")))
        # driver.get_screenshot_as_file("screenshot" + str(product[-1]) + ".png")
        score = extract_up_to_date_score(driver, True)
        print(score)
    else:
        score = extract_up_to_date_score(driver, False)
        print(score)


for prod in products:
    # fakespotProd = fakespot(prod)
    # fakespotProd.start()
    openFakespotTab(prod)
# driver.close()


# open the fakespot in chrome
# wait for text field to be loaded
# pastea mazon link
# click submit
# wait until ?
