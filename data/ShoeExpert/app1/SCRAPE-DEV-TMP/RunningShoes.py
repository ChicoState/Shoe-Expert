from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pprint import PrettyPrinter
import time

driver_path = "/usr/bin/chromedriver"
chromium_location = "/usr/bin/chromium"
domain = "runrepeat.com"
url = "https://" + domain + "/catalog/running-shoes"

# Set up Chromium options
def getChromiumOptions():
    chromium_options = Options()
    chromium_options.add_argument("--headless")
    chromium_options.add_argument("--no-sandbox")
    chromium_options.add_argument("--disable-dev-shm-usage") # /dev/shm is generally a tmpfs directory
    chromium_options.binary_location = chromium_location
    return chromium_options

# Set up the browser
def getBrowser(options):
    service = Service(driver_path)
    browser = webdriver.Chrome(service=service, options=options)
    return browser

# modify an existing cookie (deletes and recreates, cookie should be type 'dict')
def setExistingCookie(cookie, browser):
    browser.delete_cookie(cookie["name"])
    browser.add_cookie(cookie)

def getShoeNames(browser):
    page = 1
    while True:
        browser.get(url + "?page=" + str(page))
        shoe_names_xpath = "//a[@class='catalog-list-slim__names']"
        shoe_names = browser.find_elements(By.XPATH, shoe_names_xpath)
        if len(shoe_names) < 1:
            break
        for title in enumerate(shoe_names):
            print(f"{title.text}")
        page += 1

def main():
    browser = getBrowser(options=getChromiumOptions())
    browser.get(url)
    # slim list cookie
    expiration = int(time.time()) + (365 * 24 * 60 * 60) # one year
    cookie = {
        "domain": domain,
        "expiry": expiration,
        "httpOnly": False,
        "name": "list_type",
        "path": "/",
        "sameSite": "Lax",
        "secure": False,
        "value": "slim"
    }
    setExistingCookie(cookie=cookie, browser=browser)

    page = 1
    while True:
        browser.get(url + "?page=" + str(page))
        shoe_prices_xpath = "/html/body/div/div/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[4]/div"
        shoe_prices = browser.find_elements(By.XPATH, shoe_prices_xpath)

        if len(shoe_prices) < 1:
            break

        # TODO: need to extract span text inside div

        for span in enumerate(shoe_prices):
            print(f"{span.text}")

        break

        page += 1

    # Close the browser
    browser.quit()

if __name__ == "__main__":
    main()
