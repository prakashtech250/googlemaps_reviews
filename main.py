from lib2to3.pgen2.token import OP
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import logging
import riyadh_list

GM_WEBPAGE = 'https://www.google.com/maps/'

class googleMaps:
    def __init__(self, debug=True):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __get_driver(self):
        options = Options()
        if not self.debug:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notification")
        options.add_argument("--lang=en-GB")
        input_driver = webdriver.Chrome(executable_path=ChromeDriverManager(log_level=0).install(), options=options)
         # first lets click on google agree button so we can continue
        try:
            input_driver.get(GM_WEBPAGE)
            agree = WebDriverWait(input_driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "I agree")]')))
            agree.click()

            # back to the main page
            input_driver.switch_to_default_content()
        except:
            pass

        return input_driver

    def __get_logger(self):
        # create logger
        logger = logging.getLogger('googlemaps-scraper')
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        fh = logging.FileHandler('gm-scraper.log')
        fh.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # add formatter to ch
        fh.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(fh)

        return logger

    def main(self):
        urls = riyadh_list.base_url_list_a
        for url in urls:
            self.driver.get(url)
            break
        

if __name__=='__main__':
    gmap = googleMaps()
    gmap.main()