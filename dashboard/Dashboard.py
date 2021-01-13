import sys
from selenium.webdriver.support import expected_conditions as ec
from config.dashboard.Locators import Locators
from dashboard.BasePage import BasePage
from config.config import config, usernames


class Dashboard(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = config.hosts.GUI_FRONTEND

    def check_if_logged_in(self, username):
        self.find_element(Locators.user_menu_btn).click()
        user = self.find_element(Locators.user_name_in_menu).text
        self.find_element(Locators.user_menu_btn).click()
        if usernames[user] == username:
            pass
        else:
            self.logger.info(f"Dashboard:check_if_logged_in:logged user is {usernames[user]} but required {username}")
            self.browser_shutdown()
            sys.exit()

    def login(self, username="test-admin"):
        self.logger.info("Dashboard:login:starting the login")
        self.driver.get(self.url)
        self.wait_for_page_load(Locators.login_username)
        username_field = self.find_element(Locators.login_username)
        password_field = self.find_element(Locators.login_password)
        username_field.send_keys(username)
        password_field.send_keys(config.KC_PASSWORD)
        self.find_element(Locators.login_btn).click()
        self.wait.until(ec.url_contains(self.url))
        self.check_if_logged_in(username)
        self.find_element(Locators.search_device)
        self.logger.info(f"Dashboard:login:user {username} successfully logged in!")

    def check_dashboard_is_opened(self):
        return self.url in self.driver.current_url

    def check_button_presence(self, name):
        self.logger.info(f"Dashboard:check_button_presence:btn name - {name}")
        self.check_if_element_present(Locators.btn_by_name_text(name))

    def open_tab_from_navbar_menu(self, name):
        self.logger.info(f"Dashboard:open_tab_from_navbar_menu:by name - {name}")
        self.find_element(Locators.btn_by_name_text(name)).click()

    def check_import_tab(self):
        self.check_if_element_present(Locators.import_tab)

    def check_report_tab(self):
        self.check_if_element_present(Locators.report_tab)
