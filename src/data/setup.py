from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"
TIME_OUT_INIT = 20

def load_driver():
    service = Service(executable_path=CHROME_DRIVER_PATH)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920x1080")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(TIME_OUT_INIT)
    return driver
