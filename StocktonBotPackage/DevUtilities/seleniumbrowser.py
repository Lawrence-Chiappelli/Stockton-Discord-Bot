"""
A custom pseudo-API developed by me to easily
retrieve gaming lab data via web scraping- ultimately
bypassing the need for the university's credentials
to login to labstats.com
"""

from selenium import webdriver
from StocktonBotPackage.DevUtilities import configutil
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, WebDriverException
import os
import time

# -----------------------------------------+
config = configutil.get_parsed_config()  #
# -----------------------------------------+


def open_browser_driver():

    print("Opening browser driver, please wait... (this takes the longest!)")
    options = webdriver.ChromeOptions()  # executable_path="C:\Program Files\Chrome Driver\chromedriver.exe"

    num_retries = 3
    while True:
        try:
            options.binary_location = os.environ['GOOGLE_CHROME_BIN']  # Specifies the binary location for Heroku
        except KeyError:
            print(F"(Skipping binary location. Running locally.)")  # A binary location does not need to specified if the bot is running locally

        options.add_argument("--headless")  # For general purposes
        options.add_argument('--disable-gpu')  # For Heroku
        options.add_argument('--no-sandbox')  # For Heroku
        options.add_argument('--disable-dev-shm-usage')  # Hotfix found on StackOverflow

        try:
            browser = webdriver.Chrome(options=options, executable_path=os.environ['CHROME_EXE_PATH'])
        except SessionNotCreatedException as e:
            print(f"Unintended exception occurred. Retrying in 3 seconds.\nIf this exception is seen on more than one occasion, please investigate. (Is the bot running somewhere else?) Exception:\n{e}")
            continue
        except WebDriverException as wde:
            # TODO: Figure out what this is
            raise AssertionError(f"Web driver exception caught:\n{wde}")

        browser.get(config['website']['url'])

        """
        IMPORTANT: Selenium may have, very OCCASIONALLY, an issue where it
        cannot find the following specified iframes.
        Please see the workaround I've created
        """

        try:
            browser.switch_to.frame(browser.find_element_by_id(id_=config['website-iframe-ids']['frame1']))
            browser.switch_to.frame(browser.find_element_by_id(id_=config['website-iframe-ids']['frame2']))
            browser.switch_to.frame(browser.find_element_by_id(id_=config['website-iframe-ids']['frame3']))
            break
        except (NoSuchElementException, Exception) as e:
            print(f"Unknown exception caught trying to locate website iframes, retrying {num_retries} more times until success.\nException:\n{e}")
            browser.close()  # Retry the browser if there's an issue


            if num_retries == 0:
                print(F"Retries exhausted, continuing normally...")
                return None
            else:
                num_retries -= 1
                time.sleep(3)
                continue

    print("...browser driver ready for scraping!")
    return browser


# -------------------------------+
# browser = open_browser_driver()  #
# -------------------------------+
