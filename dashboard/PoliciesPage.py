from config.dashboard.Locators import Locators
from dashboard.Dashboard import Dashboard


class PoliciesPage(Dashboard):

    def check_policy_exist(self, test_policy_id):
        self.logger.info(f"PoliciesPage:check_policy_exist: {test_policy_id}")
        ids = []
        self.open_tab_from_navbar_menu("Policies")
        self.wait_for_page_load(Locators.policy_card)
        for _id in self.driver.find_elements_by_xpath(Locators.policy_id):
            ids.append(_id.text)
        return test_policy_id in ids

    def check_policy_change_btn(self):
        self.logger.info("PoliciesPage:check_policy_change_btn")
        self.check_if_element_present(Locators.policy_change_btn)

    def check_policy_definition(self):
        self.logger.info("PoliciesPage:check_policy_definition")
        self.find_element(Locators.policy_card).click()
        self.check_if_element_present(Locators.policy_definition)

    def open_policy(self):
        self.logger.info("PoliciesPage:open_policy")
        self.find_element(Locators.policy_card).click()

    def check_policies_are_shown(self):
        self.logger.info("PoliciesPage:check_policies_are_shown")
        header = self.find_element(Locators.policies_header).is_displayed()
        policy_card = self.find_element(Locators.policy_card).is_displayed()
        return header and policy_card
