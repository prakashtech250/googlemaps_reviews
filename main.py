from audioop import add
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
    location_data = {}
    def __init__(self, debug=True):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()
        self.location_data["rating"] = "NA"
        self.location_data["reviews_count"] = "NA"
        self.location_data["location"] = "NA"
        self.location_data["contact"] = "NA"
        self.location_data["website"] = "NA"
        self.location_data["Time"] = {"Monday":"NA", "Tuesday":"NA", "Wednesday":"NA", "Thursday":"NA", "Friday":"NA", "Saturday":"NA", "Sunday":"NA"}
        self.location_data["Reviews"] = []
        # self.location_data["Popular Times"] = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[], "Saturday":[], "Sunday":[]}

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

    def get_number(self):
        response = self.get_soup()
        phone = response.css('[data-tooltip="Copy phone number"] .AeaXub::text').get()
        return phone

    def get_location_data(self):
        avg_rating = self.driver.find_element(By.CLASS_NAME,"aMPvhf-fI6EEc-KVuj8d")
        total_reviews = self.driver.find_element(By.CLASS_NAME,"Yr7JMd-pane-hSRGPd")
        address = self.driver.find_element(By.CSS_SELECTOR,"[data-item-id='address']")
        # phone_number = self.driver.find_element(By.CSS_SELECTOR,"[data-tooltip='Copy phone number'] .AeaXub")
        phone_number = self.get_number()
        website = self.driver.find_element(By.CSS_SELECTOR,"[data-item-id='authority']")

        if avg_rating:
            self.location_data["rating"] = avg_rating.text
        if total_reviews:
            self.location_data["reviews_count"] = total_reviews.text[1:-1]
        if address:
            self.location_data["location"] = address.text
        if phone_number:
            self.location_data["contact"] = phone_number.text
        if website:
            self.location_data["website"] = website.text


    def click_open_close_time(self):
        if(len(list(self.driver.find_elements(By.CLASS_NAME,"LJKBpe-Tswv1b-hour-text")))!=0):
                element = self.driver.find_element(By.CLASS_NAME,"LJKBpe-Tswv1b-hour-text")
                self.driver.implicitly_wait(5)
                ActionChains(self.driver).move_to_element(element).click(element).perform()

    def get_location_open_close_time(self):
        try:
            days = self.driver.find_elements(By.CLASS_NAME,"y0skZc-header") # It will be a list containing all HTML section the days names.
            times = self.driver.find_elements(By.CLASS_NAME,"y0skZc-wZVHld") # It will be a list with HTML section of open and close time for the respective day.

            day = [a.text for a in days] # Getting the text(day name) from each HTML day section.
            open_close_time = [a.text for a in times] # Getting the text(open and close time) from each HTML open and close time section.

            for i, j in zip(day, open_close_time):
                self.location_data["Time"][i] = j

        except:
            pass


    def click_all_reviews_button(self):
        # try:
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".siAUzd-neVct-o7abwc-oXtfBe-content .wNNZR")))

        element = self.driver.find_element(By.CSS_SELECTOR,".siAUzd-neVct-o7abwc-oXtfBe-content .wNNZR")
        element.click()

        # except:
        #     self.driver.quit()
        #     return False

        return True

    def scroll_the_page(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "id-content-container"))) # Waits for the page to load.
            pause_time = 2 # Waiting time after each scroll.
            max_count = 5 # Number of times we will scroll the scroll bar to the bottom.
            x = 0

            while(x<max_count):
                scrollable_div = self.driver.find_element(By.CSS_SELECTOR,'.section-scrollbox') # It gets the section of the scroll bar.
                try:
                    self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div) # Scroll it to the bottom.
                except:
                    pass

                time.sleep(pause_time) # wait for more reviews to load.
                x=x+1

        except:
            self.driver.quit()

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

    def expand_all_reviews(self):
        try:
            element = self.driver.find_elements(By.CLASS_NAME,"ODSEW-KoToPc-ShBeI")
            for i in element:
                i.click()
        except:
            pass


    def get_reviews_data(self):

        try:
            review_names = self.driver.find_elements(By.CLASS_NAME,"ODSEW-ShBeI-title") # Its a list of all the HTML sections with the reviewer name.
            review_text = self.driver.find_elements(By.CLASS_NAME,"ODSEW-ShBeI-ShBeI-content") # Its a list of all the HTML sections with the reviewer reviews.
            review_dates = self.driver.find_elements(By.CSS_SELECTOR,".ODSEW-ShBeI-RgZmSc-date") # Its a list of all the HTML sections with the reviewer reviewed date.
            review_stars = self.driver.find_elements(By.CSS_SELECTOR,".ODSEW-ShBeI-H1e3jb") # Its a list of all the HTML sections with the reviewer rating.

            review_stars_final = []

            for i in review_stars:
                review_stars_final.append(i.get_attribute("aria-label"))

            review_names_list = [a.text for a in review_names]
            review_text_list = [a.text for a in review_text]
            review_dates_list = [a.text for a in review_dates]
            review_stars_list = [a for a in review_stars_final]


            for (a,b,c,d) in zip(review_names_list, review_text_list, review_dates_list, review_stars_list):
                self.location_data["Reviews"].append({"name":a, "review":b, "date":c, "rating":d})

        except Exception as e:
            pass

    def scrape(self, url): # Passed the URL as a variable
        # try:
        #     self.driver.get(url) # Get is a method that will tell the driver to open at that particular URL

        # except Exception as e:
        #     self.driver.quit()
        #     return

        time.sleep(2) # Waiting for the page to load.

        self.click_open_close_time() # Calling the function to click the open and close time button.
        self.get_location_data() # Calling the function to get all the location data.
        self.get_location_open_close_time() # Calling to get open and close time for each day.
        # self.get_popular_times() # Gets the busy percentage for each hour of each day.
        
        if(self.click_all_reviews_button()==False): # Clicking the all reviews button and redirecting the driver to the all reviews page.
            return

        time.sleep(5) # Waiting for the all reviews page to load.

        self.scroll_the_page() # Scrolling the page to load all reviews.
        self.expand_all_reviews() # Expanding the long reviews by clicking see more button in each review.
        self.get_reviews_data() # Getting all the reviews data.

        # self.driver.quit() # Closing the driver instance.

        # return self.location_data # Returning the Scraped Data.

    def get_soup(self):
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def main(self):
        urls = riyadh_list.base_url_list_a
        wait = WebDriverWait(self.driver, 10)
        for url in urls:
            self.driver.get(url)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'section-scrollbox')))
            hotels = self.driver.find_elements(By.CLASS_NAME, 'ZQyzS-aVTXAb')
            i = 0
            while i < len(hotels):
                hotel = hotels[i]
                hotel.click()
                time.sleep(2)
                link = self.driver.current_url
                print(link)
                data = self.scrape(link)
                print(self.location_data)
                self.driver.get(url)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'section-scrollbox')))
                hotels = self.driver.find_elements(By.CLASS_NAME, 'ZQyzS-aVTXAb')
                i+= 1
            break
        self.driver.quit()
        

if __name__=='__main__':
    gmap = googleMaps()
    gmap.main()