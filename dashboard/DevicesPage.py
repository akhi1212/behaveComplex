from selenium.webdriver.support.ui import Select
from config.dashboard.Locators import Locators
from dashboard.Dashboard import Dashboard


class DevicesPage(Dashboard):

    def search_imei(self, imei):
        self.logger.info(f"DevicesPage:search_imei:{imei}")
        if "active" not in str(self.find_element(Locators.device_tab).get_attribute("class")):
            self.find_element(Locators.device_tab).click()
        search_device = self.find_element(Locators.search_device)
        search_device.send_keys(imei)
        search_device.submit()

    def assign_policy(self, policy_id, imei):
        self.logger.info(f"DevicesPage:assign_policy: {policy_id} to {imei}")
        if imei not in self.get_imei_from_summary():
            self.search_imei(imei)
        self.find_element(Locators.assign_policy_btn).click()
        self.find_element(Locators.policy_dropdown).click()
        Select(self.find_element(Locators.policy_dropdown)).select_by_visible_text(policy_id)
        self.find_element(Locators.save_policy_assign_btn).click()

    def get_current_policy(self, do_refresh: bool = False) -> str:
        if do_refresh:
            self.driver.refresh()
            self.wait_for_device_page_is_loaded()
        return self.find_element(Locators.current_policy).text

    def check_btn_on_device_tab_is_enabled(self, name) -> bool:
        self.logger.info(f"DevicesPage:check_btn_on_device_tab_is_enabled: {name}")
        return self.check_button_is_enabled(Locators.btn_on_device_tab(name))

    def check_generate_pin_menu(self):
        self.logger.info("DevicesPage:check_generate_pin_menu")
        self.check_if_element_present(Locators.generate_pin_menu)

    def get_imei_from_summary(self) -> str:
        self.logger.info("DevicesPage:get_imei_from_summary")
        return (self.find_element(Locators.device_imei_at_summary)).text.replace(" ", "")

    def get_device_properties(self) -> dict:
        self.logger.info("DevicesPage:get_device_properties")
        self.find_element(Locators.btn_on_device_tab('Properties')).click()
        properties_list = \
            self.find_element(Locators.device_properties_table).text.replace(':\n', ' ').replace('\n', ' ').split()
        properties_dict = \
            {properties_list[i]: properties_list[i + 1] for i in range(len(properties_list) - 1) if i % 2 == 0}
        return properties_dict

    def wait_for_device_page_is_loaded(self):
        self.wait_for_page_load(Locators.device_summary_title)

    def is_device_page_opened(self) -> bool:
        return self.check_if_element_present(Locators.device_summary_title)
