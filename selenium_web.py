import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.DEBUG)

class inflow():
    def __init__(self):
        try:
            logging.debug("Initializing WebDriver...")
            service = Service("C:/Windows/chromedriver.exe")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-debugging-port=9222")

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.debug("WebDriver initialized successfully.")

        except Exception as e:
            logging.error(f"Error initializing WebDriver: {e}")
            raise

    def get_info(self, query):
        try:
            logging.debug(f"Opening Wikipedia to search for: {query}")
            self.driver.get(url='https://www.wikipedia.org')
            search = self.driver.find_element("xpath", '//*[@id="searchInput"]')
            search.send_keys(query)
            search.submit()
            logging.debug("Search completed!")

        except Exception as e:
            logging.error(f"Error during the get_info method: {e}")
            raise


assist = inflow()
assist.get_info("dhoni")
