from __future__ import annotations

from abc import ABC
import logging
from typing import Optional, List, TypeVar

from device_ui.device_controller.ui_elements.android_element import elements_factory, element_factory, AndroidUiElement
from config.config import config


class BaseAndroidScreen(ABC):
    def __init__(self, device):
        from device_ui.device_controller.device_controller import DeviceController
        self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
        self.device: DeviceController = device
        self.driver = device.driver

    def element(
            self,
            id_: Optional[str] = None,
            cls_name: Optional[str] = None,
            text: Optional[str] = None,
            text_contains: Optional[str] = None,
            descr: Optional[str] = None,
            descr_contains: Optional[str] = None,
            do_scroll: Optional[bool] = True,
            xpath: Optional[str] = None,
    ) -> AndroidUiElement:
        """
        Finds element by uiautomator2 http://appium.io/docs/en/drivers/android-uiautomator2/
        This is the preferred method. Use other methods like XPATH in exceptional cases
        """
        uia_selector_params = locals().copy()
        del uia_selector_params['self']
        return element_factory(driver=self.driver, **uia_selector_params)

    def elements(
            self,
            id_: Optional[str] = None,
            cls_name: Optional[str] = None,
            text: Optional[str] = None,
            text_contains: Optional[str] = None,
            descr: Optional[str] = None,
            descr_contains: Optional[str] = None,
            do_scroll: Optional[bool] = True,
            xpath: Optional[str] = None,

    ) -> List[AndroidUiElement]:
        """
        Finds elements by uiautomator2 http://appium.io/docs/en/drivers/android-uiautomator2/
        This is the preferred method. Use other methods like XPATH in exceptional cases
        """
        kwargs = locals().copy()
        del kwargs['self']
        return elements_factory(driver=self.driver, **kwargs)


AndroidScreen = TypeVar("AndroidScreen", bound=BaseAndroidScreen)
