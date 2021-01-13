from typing import Dict
from selenium.common.exceptions import NoSuchElementException
from device_ui.constants.android_ui_constants import KNOXGUARGCONSTANTS as KC
from device_ui.device_controller.security_app_controllers.base_classes.base_android_screen import BaseAndroidScreen
from device_ui.device_controller.security_app_controllers.base_classes.base_security_app_controller import BaseSecurityAppUiController
from device_ui.device_controller.ui_elements.android_element import AndroidUiElement


class KnoxGuardUiController(BaseSecurityAppUiController):
    def __init__(self, device):
        super().__init__(device=device)
        self.home_screen = KnoxGuardHomeScreen(device=self.device)

    def is_screen_locked(self) -> bool:
        if not self.home_screen.is_open():
            return False
        self.device.press_button("home")
        return self.home_screen.is_open()

    def start(self):
        pass

    def get_size(self) -> Dict[str, int]:
        """
        {'height': int, 'width': int}
        """
        root_element = self.element(cls_name=KC.ROOT_CLASS.value)
        assert root_element.get_attribute("package") == KC.PACKAGE.value
        return root_element.size


class KnoxGuardHomeScreen(BaseAndroidScreen):
    def get_main_element(self) -> AndroidUiElement:
        return self.element(id_=KC.HOME_SCREEN.value)

    def is_open(self) -> bool:
        try:
            self.get_main_element()
        except NoSuchElementException:
            return False
        else:
            return True

    def get_message(self) -> Dict[str, str]:
        return {
            "title": self.element(id_=KC.MESSAGE_TITLE.value).get_text(),
            "text": self.element(id_=KC.MESSAGE_TEXT.value).get_text(),
        }

    def click_ok_btn(self):
        self.element(id_=KC.OK_BTN.value).tap()
