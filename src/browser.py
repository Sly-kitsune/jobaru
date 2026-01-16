import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserEngine:
    def __init__(self, headless=False):
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)

    def _setup_driver(self, headless):
        print("   [DEBUG] Setting up Chrome options...")
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        # Performance / Space optimizations
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        
        # User agent to avoid immediate bot detection (basic)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        print("   [DEBUG] Installing/Checking Chrome Driver...")
        try:
            path = ChromeDriverManager().install()
            print(f"   [DEBUG] Driver path: {path}")
        except Exception as e:
            print(f"   [DEBUG] Error installing driver: {e}")
            raise e

        print("   [DEBUG] Initializing WebDriver...")
        try:
            service = Service(path)
            driver = webdriver.Chrome(service=service, options=options)
            driver.maximize_window()
            print("   [DEBUG] WebDriver initialized successfully.")
            return driver
        except Exception as e:
            print(f"   [DEBUG] Error initializing WebDriver: {e}")
            raise e

    def navigate(self, url):
        self.driver.get(url)
        time.sleep(2)  # Basic wait for render

    def current_url(self):
        return self.driver.current_url

    def get_source(self):
        return self.driver.page_source

    def quit(self):
        if self.driver:
            self.driver.quit()

    def find_element(self, selector, by=By.CSS_SELECTOR):
        try:
            return self.driver.find_element(by, selector)
        except:
            return None

    def find_elements(self, selector, by=By.CSS_SELECTOR):
        return self.driver.find_elements(by, selector)

    def click(self, selector, by=By.CSS_SELECTOR):
        try:
            el = self.wait.until(EC.element_to_be_clickable((by, selector)))
            el.click()
            return True
        except Exception as e:
            logging.warning(f"Failed to click {selector}: {e}")
            return False

    def type_text(self, selector, text, by=By.CSS_SELECTOR):
        try:
            el = self.wait.until(EC.visibility_of_element_located((by, selector)))
            el.clear()
            el.send_keys(text)
            return True
        except Exception as e:
            logging.warning(f"Failed to type in {selector}: {e}")
            return False
