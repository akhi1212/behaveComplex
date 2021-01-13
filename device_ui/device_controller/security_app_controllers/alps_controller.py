from __future__ import annotations

from typing import Dict

from selenium.common.exceptions import NoSuchElementException

from device_ui.adb_controller.packages import PACKAGES
from device_ui.constants.android_ui_constants import ALPSCONSTANTS as AC
from device_ui.device_controller.security_app_controllers.base_classes.base_android_screen import BaseAndroidScreen
from device_ui.device_controller.security_app_controllers.base_classes.base_security_app_controller import BaseSecurityAppUiController
from device_ui.device_controller.ui_elements.android_element import AndroidUiElement


class AlpsUiController(BaseSecurityAppUiController):
    def __init__(self, device):
        super().__init__(device=device)
        self.home_screen = AlpsHomeScreen(device=self.device)
        self.maintenance_menu = MaintenanceMenu(device=self.device)

    def is_screen_locked(self) -> bool:
        if not self.home_screen.is_open():
            return False
        self.device.press_button("home")
        return self.home_screen.is_open()

    def start(self):
        alps_pkg = PACKAGES["ALPS"]
        self.device.start_activity(
            package=alps_pkg.name,
            activity=alps_pkg.activities["Main"],
        )

    def get_size(self) -> Dict[str, int]:
        """
        >>> self.get_size()
        {'height': int, 'width': int}
        """
        root_element = self.element(cls_name=AC.ROOT_CLASS.value)
        assert root_element.get_attribute("package") == AC.PACKAGE.value
        return root_element.size


class AlpsHomeScreen(BaseAndroidScreen):
    def get_main_element(self) -> AndroidUiElement:
        return self.element(id_=AC.ACTION_BAR_ROOT.value)

    def is_open(self) -> bool:
        try:
            self.get_main_element()
        except NoSuchElementException:
            return False
        else:
            return True

    def get_icon_home(self) -> AndroidUiElement:
        return self.element(AC.ICON_HOME.value)

    def press_icon_home(self) -> AlpsHomeScreen:
        self.get_icon_home().tap()
        return self

    def get_message(self) -> Dict[str, str]:
        return {
            "title": self.element(id_=AC.MESSAGE_TITLE.value).get_text(),
            "text": self.element(id_=AC.MESSAGE_TEXT.value).get_text(),
        }


class MaintenanceMenu(BaseAndroidScreen):
    def tap_check_in(self) -> MaintenanceMenu:
        self.element(id_=AC.MAINTENANCE_CHECKIN.value, do_scroll=False).tap()
        return self
