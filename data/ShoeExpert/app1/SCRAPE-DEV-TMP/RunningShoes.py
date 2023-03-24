# TODO: continue integrating functions into class starting from line 214

from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import PrettyPrinter
import tempfile
import time

class ScraperSingleton:
    __driver_path = "/usr/bin/chromedriver"
    __chromium_location = "/usr/bin/chromium"
    __domain = "runrepeat.com"
    __url = "https://" + __domain + "/catalog/running-shoes"
    __browser = None
    __wait = 15
    __sleep = 1
    __column_filter_dict = None
    __csv_data = []

    class __ColumnSelector(Enum):
        SCORE = "fact-score"
        EXPERT_RATING = "fact-expert_score"
        USERS_RATING = "fact-users_score"
        MSRP = "fact-msrp_formatted"
        SALES_PRICE = "fact-price"
        RELEASE_DATE = "fact-release-date"
        REVIEW_TYPE = "fact-review-type"
        REVIEWS_COUNT = "fact-number-of-reviews"
        TERRAIN = "fact-terrain"
        PACE = "fact-pace"
        BRAND = "fact-brand"
        ARCH_SUPPORT = "fact-arch-support"
        HEEL_TOE_DROP = "fact-heel-to-toe-drop"
        WEIGHT = "fact-weight"
        TOEBOX = "fact-toebox"
        PRONATION = "fact-pronation"
        FEATURES = "fact-features"
        USE = "fact-use"
        DISTANCE = "fact-distance"
        CUSHIONING = "fact-cushioning"
        TYPE = "fact-type"
        WIDTH = "fact-width"
        STRIKE_PATTERN = "fact-strike-pattern"
        FOOT_CONDITION = "fact-foot-condition"
        COLLECTION = "fact-collection"
        FLEXIBILITY = "fact-flexibility"
        ARCH_TYPE = "fact-arch-type"
        TECHNOLOGY = "fact-technology"
        WATERPROOFING = "fact-waterproofing"
        MATERIAL = "fact-material"
        FOREFOOT_HEIGHT = "fact-forefoot-height"
        HEEL_HEIGHT = "fact-heel-height"
        SEASON = "fact-season"
        SUMMER = "fact-summer"
        ULTRA_RUNNING = "fact-ultra-running"

        def get_selector(self):
            return (By.CSS_SELECTOR, f"input[type='checkbox'][id='{self.value}'] + span.checkbox")

        @staticmethod
        def get_full_list(exclude=None):
            if exclude is None:
                exclude = []
            return [column_selector.get_selector() for column_selector in ScraperSingleton.__ColumnSelector if column_selector not in exclude]

        @staticmethod
        def get_empty_list(include=None):
            if include is None:
                include = []
            return [column_selector.get_selector() for column_selector in include if isinstance(column_selector, ScraperSingleton.__ColumnSelector)]

        @staticmethod
        def get_default_map():
            default_map = {}
            for member in ScraperSingleton.__ColumnSelector:
                default_map[member] = False
            default_map[ScraperSingleton.__ColumnSelector.MSRP] = True
            return default_map

        @staticmethod
        def get_false_map():
            false_map = ScraperSingleton.__ColumnSelector.get_default_map()
            false_map[ScraperSingleton.__ColumnSelector.MSRP] = False
            return false_map

        @staticmethod
        def get_true_map():
            true_map = ScraperSingleton.__ColumnSelector.get_false_map()
            for key in true_map:
                true_map[key] = True
            return true_map


    # Set up the browser
    @classmethod
    def __initBrowser(cls):
        service = Service(cls.__driver_path)
        browser = webdriver.Chrome(service=service, options=cls.__getChromiumOptions())
        browser.delete_all_cookies()
        cls.__browser = browser

    def __new__(cls):
        if cls.__browser is None:
            cls.__initBrowser()
        return cls.__browser

    def __init__(self):
        pass

    # Set up Chromium options
    @classmethod
    def __getChromiumOptions(cls):
        chromium_options = Options()
        # chromium_options.add_argument("--headless")
        chromium_options.add_argument("--no-sandbox")
        chromium_options.add_argument("--disable-dev-shm-usage") # /dev/shm is generally a tmpfs directory
        # Create a temporary directory for the user data
        temp_profile_dir = tempfile.mkdtemp()
        # Add the user data directory argument
        chromium_options.add_argument(f"--user-data-dir={temp_profile_dir}")
        chromium_options.binary_location = cls.__chromium_location
        return chromium_options

    @classmethod
    def __getColumnFilterDict(cls):
        if cls.__column_filter_dict is None:
            cls.__column_filter_dict = cls.__ColumnSelector.get_default_map()
        return cls.__column_filter_dict

    @classmethod
    def __setColumnFilterDict(cls, dict):
        if cls.__column_filter_dict is None:
            cls.__column_filter_dict = cls.__ColumnSelector.get_default_map()
        for key, value in dict.items():
            if isinstance(key, cls.__ColumnSelector):
                if isinstance(value, bool):
                    cls.__column_filter_dict[key] = value
                else:
                    raise TypeError(f"Expected bool, but received {type(value)}")
            else:
                raise TypeError(f"Expected ScraperSingleton.__ColumnSelector enumeration member, but received {type(key)}")

    # dev function to output page source
    @classmethod
    @PendingDeprecationWarning
    def __outputPageSource(cls, filename):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(cls.__browser.page_source)

    # dev function to check cookies
    @classmethod
    @PendingDeprecationWarning
    def __printCookies(cls, cookie_name=""):
        if cookie_name == "":
            PrettyPrinter(indent=4).pprint(cls.__browser.get_cookies())
        else:
            PrettyPrinter(indent=4).pprint(cls.__browser.get_cookie(cookie_name))

    @classmethod
    def __wait_and_click(cls, selector):
        element = WebDriverWait(cls.__browser, cls.__wait).until(EC.element_to_be_clickable(selector))
        element.click()

    @classmethod
    def __scroll_and_click(cls, selector):
        element = WebDriverWait(cls.__browser, cls.__wait).until(EC.presence_of_element_located(selector))
        browser.execute_script("arguments[0].click();", element)

    # Change view to table
    @classmethod
    def __getSlimListView(cls):
        cookie = cls.__browser.get_cookie("list_type")
        if cookie is None or cookie["value"] != "slim" or cookie["expiry"] < time.time():
            cls.__wait_and_click(selector=(By.CSS_SELECTOR, "svg.slim-view-icon.catalog__list-tab-icon"))

    @classmethod
    def __applyColumns(cls):
        cls.__wait_and_click(selector=(By.CSS_SELECTOR, "button.buy_now_button[data-v-795eb1ee]"))

    @classmethod
    def __editColumns(cls):
        cls.__wait_and_click(selector=(By.CSS_SELECTOR, "button.buy_now_button.edit-columns__button"))
        time.sleep(cls.__sleep)

    @classmethod
    def __getEmptyView(cls):
        cls.__editColumns()
        checkboxes = [] # cls.__ColumnSelector.get_full_list(exclude = [cls.__ColumnSelector.MSRP])
        for key in cls.__getColumnFilterDict():
            if cls.__getColumnFilterDict()[key]:
                checkboxes.append(key.get_selector())
        for selector in checkboxes:
            cls.__scroll_and_click(selector=selector)
        cls.__applyColumns()
        cls.__setColumnFilterDict(cls.__ColumnSelector.get_false_map())

    @classmethod
    def __getColumnsView(cls, list):
        cls.__getEmptyView()
        cls.__editColumns()
        for item in list:
            if isinstance(item, cls.__ColumnSelector):
                cls.__scroll_and_click(selector=item.get_selector())
            else:
                raise TypeError(f"Expected ScraperSingleton.__ColumnSelector enumeration member, but received {type(item)}")
        cls.__applyColumns()
        cls.__setColumnFilterDict({k: True for k in list})

    @classmethod
    def getShoeNames(cls):
        page = 1
        while True:
            browser.get(url + "?page=" + str(page))
            shoe_names = browser.find_elements(By.CLASS_NAME, "catalog-list-slim__names")
            if len(shoe_names) < 1:
                break
            for title in shoe_names:
                print(f"{title.text}")
            page += 1

    def getColumnData():
        global browser, url
        page = 1
        while True:
            browser.get(url + "?page=" + str(page))
            getEmptyView()
            getMSRPView()
            sales_prices = browser.find_elements(By.CSS_SELECTOR, "div.catalog-list-slim__facts__column div.catalog-list-slim__shoes-fact__values span")
            if len(sales_prices) < 1:
                break
            for price in sales_prices:
                print(f"{price.text}")

            break # FIXME:

            page += 1

def main():
    global browser
    initBrowser(options=getChromiumOptions())
    browser.get(url)
    getSlimListView()
    getColumnData()

    # Close the browser
    browser.quit()

if __name__ == "__main__":
    main()
