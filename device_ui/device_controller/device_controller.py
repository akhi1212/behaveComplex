from __future__ import annotations

import logging
from typing import Dict, Tuple

from behave.runner import Context
from appium import webdriver
from urllib3.exceptions import MaxRetryError
from appium.webdriver.extensions.android.nativekey import AndroidKey

from config.device_ui import settings
from device_ui.adb_controller.adb_controller import AdbController, DeviceInfo
from device_ui.device_controller.security_app_controllers.alps_controller import AlpsUiController
from device_ui.device_controller.security_app_controllers.base_classes.base_security_app_controller import SecurityAppController
from device_ui.device_controller.security_app_controllers.knox_guard_controller import KnoxGuardUiController
from device_ui.device_controller.settings import get_settings_instance

from config.config import config


class DeviceController:
    def __init__(self, context: Context, do_press_home: bool = False):
        self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
        self.context = context
        self.adb: AdbController = context.adb
        self.info: DeviceInfo = self.context.adb.get_device_info()
        self.driver: webdriver = self.__get_driver()
        self.security_app: SecurityAppController = self.__get_security_app()
        self.settings = get_settings_instance(context=context, device=self)
        if do_press_home:
            self.press_button("home")

    def __get_security_app(self) -> SecurityAppController:
        assert self.info.manufacturer and self.info.android_version
        if self.info.manufacturer == "samsung":
            security_app = KnoxGuardUiController(device=self)
        else:
            security_app = AlpsUiController(device=self)
        self.logger.debug(f"Set device.security_app to {security_app.__class__.__name__}")
        return security_app

    def __get_driver(self) -> webdriver:
        des_cap = settings.DESIRED_CAPABILITIES
        des_cap["platformVersion"] = self.info.android_version
        try:
            driver = webdriver.Remote(
                command_executor=settings.APPIUM_ADDRESS,
                desired_capabilities=des_cap,
            )
        except MaxRetryError as e:
            raise ConnectionError(f"Appium server not found at {settings.APPIUM_ADDRESS}\n{e}")
        else:
            self.logger.info(f"Start Appium session {driver.session_id}")
            return driver

    def start_activity(self, package: str, activity: str) -> DeviceController:
        self.logger.debug(f"Start activity {package} {activity}")
        self.driver.start_activity(app_package=package, app_activity=activity)
        return self

    def execute_mobile(self, command: str, *options) -> Dict[str, str]:
        """
        executes shell command
        :return: The command's JSON response loaded into a dictionary object.
        """
        return self.driver.execute_script(f"mobile: {command}", *options)

    def disconnect(self) -> DeviceController:
        self.logger.info(f"Stop Appium session {self.driver.session_id}")
        self.driver.quit()
        return self

    def press_button(self, name: str) -> DeviceController:
        """
        :param name: any key from `key_map` or `AndroidKey`
        """
        key_map = dict(
            home=AndroidKey.HOME,
            back=AndroidKey.BACK,
            recent_apps=AndroidKey.APP_SWITCH,
            vol_up=AndroidKey.VOLUME_UP,
            vol_down=AndroidKey.VOLUME_DOWN,
            power=AndroidKey.POWER,
        )
        try:
            key_code = key_map[name]
        except KeyError:
            key_code = getattr(AndroidKey, name)

        self.driver.press_keycode(keycode=key_code)
        return self

    def save_screenshot(self, dest: str) -> DeviceController:
        """
        Takes screenshot of the current view
        :param dest: abs path to the destination file to which the screenshot is to be saved. The extension must be .png
        """
        self.logger.info(f"Save screenshot: {dest}")
        self.driver.get_screenshot_as_file(dest)
        return self

    def get_screen_resolution(self) -> Dict[str, int]:
        return self.driver.get_window_size()

    def get_locale(self) -> Tuple[str, str]:
        locale = self.adb.execute(f"adb -s {self.info.serial_number} shell getprop persist.sys.locale").strip()
        language, country = locale.split("-")
        return language, country

    def is_locked(self) -> bool:
        """
        Tells if the device is locked by a normal short-press of the power button
        """
        return self.driver.is_locked()

    def is_screen_locked(self) -> bool:
        """
        Tells if the device is locked by the security app
        """
        return self.security_app.is_screen_locked()

    def get_screen_size(self) -> Dict[str, int]:
        """
        >>> self.get_screen_size()
        {'height': int, 'width': int}
        """
        return self.driver.get_window_size()
