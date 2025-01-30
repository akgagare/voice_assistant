import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager  # ✅ Auto-manage ChromeDriver

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Inflow:
    def __init__(self):
        try:
            logging.debug("Initializing WebDriver...")

            options = Options()
            options.add_argument("--headless")  # ✅ Runs in headless mode (optional)
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # ✅ Professional way to initialize WebDriver
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            logging.debug("WebDriver initialized successfully.")

        except Exception as e:
            logging.error(f"Error initializing WebDriver: {e}")
            raise

    def get_info(self, query):
        try:
            logging.debug(f"Opening Wikipedia to search for: {query}")
            self.driver.get('https://www.wikipedia.org')

            search = self.driver.find_element(By.XPATH, '//*[@id="searchInput"]')
            search.send_keys(query)
            search.submit()

            logging.debug("Search completed!")

        except Exception as e:
            logging.error(f"Error during the get_info method: {e}")
            raise

if __name__ == "__main__":
    assist = Inflow()
    assist.get_info("dhoni")
