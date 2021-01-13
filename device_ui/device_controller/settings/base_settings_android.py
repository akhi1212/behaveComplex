from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TypeVar, List

from selenium.common.exceptions import NoSuchElementException

from device_ui.adb_controller.packages import PACKAGES
from device_ui.device_controller.ui_elements.android_element import AndroidUiElement
from device_ui.device_controller.ui_elements.xpath_selector import get_parent_last_child_xpath
from device_ui.device_controller.security_app_controllers.base_classes.base_android_screen import BaseAndroidScreen
from device_ui.constants.android_ui_constants import SETTINGS as SC


class BaseSettingsAndroid(BaseAndroidScreen):
    manufacturer: str = ""
    android_version: str = ""

    def open(self, menu: str = "Settings") -> SettingsAndroid:
        """
        Opens menu in settings by starting ADB activity
        :param menu: must be one of the keys in device_ui.adb_controller.packages.PACKAGES
        """

        self.logger.info(f"Open settings -> {menu}")
        pkg = PACKAGES[self.device.info.manufacturer][self.device.info.android_version]["Settings"]
        self.device.start_activity(package=pkg.name, activity=pkg.activities[menu])
        return self

    def open_app_info(self, app_name: str) -> SettingsAndroid:
        pkg = PACKAGES[app_name].name
        act = PACKAGES[self.device.info.manufacturer][self.device.info.android_version]["Settings"].activities["Info"]
        self.device.adb.execute(f"adb shell am start -a {act} -d package:{pkg}")
        return self

    def tap_gear(self) -> SettingsAndroid:
        self.element(id_=SC.GEAR.value).tap()
        return self

    def tap_menu(self, name: str) -> SettingsAndroid:
        """
        Scrolls to the menu with name `name` and taps it
        :param name: the text that is written in the menu on bold font
        """
        menu = self.__get_menu(name=name)
        menu.tap()
        return self

    def toggle_switch(self, menu_name: str, on: Optional[bool] = None) -> SettingsAndroid:
        """
        Finds the switch in menu with name `menu_name`, and sets it to ON if `on` is True, or to OFF if `on` is False.
        If `on` is None - just clicks the switch, disregarding its initial state.
        :param menu_name: the text that is written in the menu on bold font
        :param on: Optional (the desired state of the switch)
        """
        switch = self.__get_switch(menu_name)
        if on is None:
            switch.tap()
        else:
            is_on = switch.is_checked()
            if is_on != on:
                switch.tap()

        return self

    def is_switch_on(self, menu_name: str) -> bool:
        """
        Scrolls to menu with name `menu_name`, finds a switch in the menu, checks its state and returns it
        :param menu_name: the text that is written in the menu on bold font
        :return True if the switch is ON, otherwise False
        """
        switch = self.__get_switch(menu_name)
        return switch.is_checked()

    def __get_menu(self, name: str) -> AndroidUiElement:
        """
        In the current page, finds the menu with name `menu_name` (scrolls if necessary)
        :param name: the text that is written in the menu on bold font
        """
        _ = self.element(text=name)  # scroll to the menu
        try:
            menu = self.__get_menu_by_uiautomator(name=name)
        except NoSuchElementException:
            menu = self.__get_menu_by_xpath(name=name)
        return menu

    def __get_menu_by_uiautomator(self, name: str) -> AndroidUiElement:
        recycler = self.element(cls_name=SC.RECYCLER.value, do_scroll=False)
        table_layouts = recycler.elements(cls_name="android.widget.TableLayout")
        linear_layouts = recycler.elements(cls_name="android.widget.LinearLayout")
        frame_layouts = recycler.elements(cls_name="android.widget.FrameLayout")

        menus = table_layouts + linear_layouts + frame_layouts
        for menu in menus:
            try:
                _ = menu.element(text=name)  # does the menu have the text?
            except NoSuchElementException:
                continue
            else:
                return menu

    def __get_menu_by_xpath(self, name):
        xpath = get_parent_last_child_xpath(parent_step=2, from_el_with_text=name)
        android_element = self.element(xpath=xpath)
        return android_element

    def __get_switch_by_uiautomator(self, menu_name: str) -> AndroidUiElement:
        try:
            switch = self.element(cls_name="android.widget.Switch", text=menu_name, do_scroll=False)
        except NoSuchElementException:
            menu = self.__get_menu_by_uiautomator(name=menu_name)
            switches = menu.elements(cls_name="android.widget.Switch")
            assert len(switches) == 1
            switch = switches[0]
        return switch

    def __get_switch_by_xpath(self, menu_name: str) -> AndroidUiElement:
        xpath = get_parent_last_child_xpath(parent_step=2, from_el_with_text=menu_name, child_step=2)
        android_element = self.element(xpath=xpath)
        return android_element

    def __get_switch(self, menu_name: str):
        """
        In the current page, finds the menu with name `menu_name` (scrolls if necessary)
        Then, inside the found menu, finds elements with class "android.widget.Switch"
        If the quantity of found elements == 1, returns the element
        :param menu_name: the text that is written in the menu on bold font
        """
        _ = self.element(text=menu_name)  # scroll to the menu
        try:
            switch = self.__get_switch_by_uiautomator(menu_name=menu_name)
        except NoSuchElementException:
            switch = self.__get_switch_by_xpath(menu_name=menu_name)
        return switch


SettingsAndroid = TypeVar("SettingsAndroid", bound=BaseSettingsAndroid)
