import os
import logging
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

from config.config import config, get_csv_download_dir


class BasePage:

    def __new__(cls, driver):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, driver):
        self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
        self.driver = driver
        self.timeout = config.web_ui_wait_timeout
        self.wait = WebDriverWait(self.driver, self.timeout)

    def find_element(self, locator):
        try:
            return self.wait.until(ec.presence_of_element_located(locator))
        except TimeoutException:
            self.logger.info(f"BasePage:find_element:Timed out waiting for page to load for {locator}")

    def browser_shutdown(self):
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.info("BasePage:browser_shutdown:" + str(e.args))

    def wait_for_page_load(self, locator):
        try:
            self.wait.until(ec.presence_of_element_located(locator))
        except TimeoutException:
            self.logger.info("BasePage:wait_for_page_load:Timed out waiting for page to load")
            self.browser_shutdown()

    def check_if_element_present(self, locator):
        try:
            self.wait.until(ec.presence_of_element_located(locator)).is_displayed()
            return True
        except TimeoutException:
            return False

    def check_button_is_enabled(self, locator):
        return self.find_element(locator).is_enabled()

    def wait_for_selector_options(self, selector):
        try:
            self.wait.until(selector_options_exists(selector))
            return True
        except TimeoutException:
            return False

    def wait_for_download(self, timeout, file_name):
        report_path = os.path.join(get_csv_download_dir(), file_name)
        start = time.perf_counter()
        while time.perf_counter() - start <= timeout:
            if os.path.exists(report_path):
                break
            time.sleep(1)


class selector_options_exists(object):

    def __init__(self, selector):
        self.selector = selector

    def __call__(self, driver):
        elements = driver.find_elements_by_css_selector(self.selector)
        if len(elements) > 1:
            return True
        return False

