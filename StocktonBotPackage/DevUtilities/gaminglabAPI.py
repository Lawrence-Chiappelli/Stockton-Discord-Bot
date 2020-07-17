"""
A custom pseudo-API developed by me to easily
retrieve gaming lab data via websraping- ultimately
bypassing the need for the university's credentials
to login to labstats.com
"""

from selenium import webdriver
from StocktonBotPackage.DevUtilities import configparser
import os

# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------+


def open_browser_driver():

    print("Opening browser driver, please wait...")
    options = webdriver.ChromeOptions()  # executable_path="C:\Program Files\Chrome Driver\chromedriver.exe"

    try:
        options.binary_location = os.environ['GOOGLE_CHROME_BIN']  # Specifies the binary location for Heroku
    except Exception:
        pass

    options.add_argument("--headless")  # For general purposes
    options.add_argument('--disable-gpu')  # For Heroku
    options.add_argument('--no-sandbox')  # For Heroku
    options.add_argument('--disable-dev-shm-usage')  # Hotfix found on StackOverflow
    browser = webdriver.Chrome(options=options, executable_path=os.environ['CHROME_EXE_PATH'])

    browser.get(config['website']['url'])
    browser.switch_to.frame(browser.find_element_by_id(id_=config['website-iframe-ids']['frame1']))
    browser.switch_to.frame(browser.find_element_by_id(id_=config['website-iframe-ids']['frame2']))
    browser.switch_to.frame(browser.find_element_by_id(id_=config['website-iframe-ids']['frame3']))
    print("...browser driver ready for scraping!")
    return browser


# -------------------------------+
browser = open_browser_driver()  #
# -------------------------------+


def get_pc_availability():

    try:

        pc_statuses = {}
        for i in range(1, int(config['lab']['pc_amount'])+1):  # Plus 1, because for i in range is inclusive
            element = browser.find_element_by_id(id_=config['lab-pc-tags'][f'{str(i)}'])
            attribute = element.get_attribute("style")
            if config['lab']['available'] in str(attribute):
                pc_statuses[f'pc{i}'] = ['available']
            else:
                pc_statuses[f'pc{i}'] = ['inuse']

        return pc_statuses

    except Exception as exception:
        print(f"Could not find browser attribute:\n{exception}")
        browser.quit()  # Try restarting the browser if there's an issue
        open_browser_driver()

    return None
