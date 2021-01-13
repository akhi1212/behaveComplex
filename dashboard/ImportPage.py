import os

from config.dashboard.Locators import Locators
from dashboard.Dashboard import Dashboard


class ImportPage(Dashboard):

    def register(self, csv_file_path):
        self.logger.info(f"ImportPage:register: import file {csv_file_path}")
        self.open_tab_from_navbar_menu("Import")
        self.find_element(Locators.register_btn).click()
        self.find_element(Locators.select_file_input).send_keys(os.path.abspath(csv_file_path))
        self.find_element(Locators.upload_confirm_chkbox).click()
        assert self.check_button_is_enabled(Locators.upload_btn)
        self.find_element(Locators.upload_btn).click()

    def get_upload_result_message(self):
        msg = self.find_element(Locators.upload_result_alert).text
        self.logger.info(f"ImportPage:get_upload_result_message: Result: {msg}")
        return msg
