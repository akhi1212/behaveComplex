from config.dashboard.Locators import Locators
from dashboard.Dashboard import Dashboard
from selenium.webdriver.support.select import Select


class ReportPage(Dashboard):
    """
    Class representing Reports page of ALPS Dashboard
    """
    def select_report_to_download(self, policy_name):
        self.open_tab_from_navbar_menu("Reports")
        self.logger.info(f"ReportPage:select: select device report by name {policy_name}")
        selector = Select(self.find_element(Locators.device_report_selector))
        self.wait_for_selector_options(Locators.device_report_selector[1])
        for option in selector.options:
            if option.text == "/{}".format(policy_name):
                selector.select_by_visible_text(option.text)

    def download_csv_report(self, policy_name):
        self.logger.info(f"ReportPage:download: download device report by state {policy_name}")
        assert self.check_button_is_enabled(Locators.csv_download_button) is True
        self.find_element(Locators.csv_download_button).click()
        self.wait_for_download(5, "_" + policy_name)
