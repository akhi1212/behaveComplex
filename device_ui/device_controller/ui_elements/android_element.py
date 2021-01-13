from __future__ import annotations

import pprint
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Union, Set

from appium import webdriver
from appium.webdriver import WebElement
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from config.device_ui import settings
from device_ui.device_controller.ui_elements.androd_ui_selector import get_android_selector
from config.config import config


def element_factory(
        driver: webdriver,
        explicit_element: Optional[Union[WebElement, List[WebElement]]] = None,
        search_context: Optional[Union[webdriver, WebElement]] = None,
        uia_selector: Optional[str] = None,
        xpath: Optional[str] = None,
        expected_conditions: Optional[Set[type]] = None,
        **uia_selector_params,
) -> AndroidUiElement:
    """
    :param driver:
    :param explicit_element: if specified, no search will be made. The explicit_element will be just wrapped.
    :param search_context: if not specified, search will be made in the entire page (i.e. driver.find...())
        otherwise, the search will be made in the specified search context (i.e. self.wrapped_object.find...())
    :param uia_selector: can override automatic uia selector creation from uia_selector_params
    :param xpath: will lead to search being made by xpath
    :param expected_conditions: can override default expected conditions
    :param uia_selector_params: id_ / cls_name / text / text_contains / descr / descr_contains
    """
    return AndroidUiElement(
        driver=driver,
        explicit_element=explicit_element,
        search_context=search_context,
        uia_selector=uia_selector,
        xpath=xpath,
        expected_conditions=expected_conditions,
        **uia_selector_params,
    )


def elements_factory(
        driver: webdriver,
        explicit_element: Optional[Union[WebElement, List[WebElement]]] = None,
        search_context: Optional[Union[webdriver, WebElement]] = None,
        uia_selector: Optional[str] = None,
        xpath: Optional[str] = None,
        expected_conditions: Optional[Set[type]] = None,
        **uia_selector_params,
) -> List[AndroidUiElement]:
    """
    :param driver:
    :param explicit_element: if specified, no search will be made. The explicit_element will be just wrapped.
    :param search_context: if not specified, search will be made in the entire page (i.e. driver.find...())
        otherwise, the search will be made in the specified search context (i.e. self.wrapped_object.find...())
    :param uia_selector: can override automatic uia selector creation from uia_selector_params
    :param xpath: will lead to search being made by xpath
    :param expected_conditions: can override default expected conditions
    :param uia_selector_params: id_ / cls_name / text / text_contains / descr / descr_contains
    """
    elements = []
    elements_collection = AndroidUiElementCollection(
        driver=driver,
        explicit_element=explicit_element,
        search_context=search_context,
        uia_selector=uia_selector,
        xpath=xpath,
        expected_conditions=expected_conditions,
        **uia_selector_params,
    )
    for element in elements_collection:
        element = AndroidUiElement(driver=driver, explicit_element=element)
        elements.append(element)
    return elements


class BaseAndroidElement(ABC):
    def __init__(
            self,
            driver: webdriver,
            explicit_element: Optional[Union[WebElement, List[WebElement]]] = None,
            search_context: Optional[Union[webdriver, WebElement]] = None,
            uia_selector: Optional[str] = None,
            xpath: Optional[str] = None,
            expected_conditions: Optional[Set[type]] = None,
            **uia_selector_params,
    ):
        self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
        self.driver: webdriver = driver
        self.search_context = search_context or driver
        self.wait_type = By.XPATH if xpath is not None else MobileBy.ANDROID_UIAUTOMATOR
        self.selector_params = uia_selector_params
        self.selector = self._get_selector(xpath=xpath, uia_selector=uia_selector)
        self.find_method = self._get_find_method()
        self.expected_conditions = expected_conditions or self._get_default_ec()
        self.wrapped_object = explicit_element if explicit_element is not None else self.get_wrapped_object()

    def __getattr__(self, item):
        """
        Redirect unknown callbacks to self.wrapped_object like
        send_keys(), set_text(), set_value(), screenshot(), etc. For full list see WebElement.
        Examples:
            >>> element = self.element(id_="some id")
            >>> element.set_text("some_text")
            or just
            >>> self.element(id_="some id").set_text("some_text")
        """
        if item == "click":
            if "tap" in self.__dir__():
                return self.tap
        elif "wrapped_object" in self.__dict__:
            if hasattr(self.wrapped_object, item):
                return getattr(self.wrapped_object, item)
            else:
                import traceback
                trace: List[str] = traceback.format_stack()
                self.logger.debug(f"{self.wrapped_object} has no attribute {item}")
                stack = ""
                for line in trace:
                    stack += line
                self.logger.debug(stack)

    def __eq__(self, other) -> bool:
        return self.wrapped_object == other.wrapped_object

    def __repr__(self):
        if "wrapped_object" in self.__dict__:
            return str(self.wrapped_object)
        else:
            return self.selector

    @abstractmethod
    def _get_default_ec(self) -> Set[type]:
        """
        these conditions will be used if no expected_conditions are passed to the class
        """

    @abstractmethod
    def _get_find_method(self) -> callable:
        """
        these conditions will be used if no expected_conditions are passed to the class
        """

    def _get_selector(self, xpath: Optional[str], uia_selector: Optional[str]) -> str:
        return xpath or uia_selector or get_android_selector(**self.selector_params)

    def wait(self):
        for exp_cond in self.expected_conditions:
            method = exp_cond(locator=(self.wait_type, self.selector))
            wait_ = WebDriverWait(self.driver, settings.WAIT_TIMEOUT)
            try:
                wait_.until(method=method, message=self.selector)
            except TimeoutException as e:
                raise NoSuchElementException(f"{self.selector}\n{e}")

    def get_wrapped_object(self, selector: Optional[str] = None) -> Union[WebElement, List[WebElement]]:
        self.wait()
        object_ = self.find_method(selector or self.selector)
        return object_


class AndroidUiElement(BaseAndroidElement):
    """
    This is basically a wrapper around selenium's WebElement
    All WebElement's attributes and methods can be reached directly, even if they are not implemented in this or
    base class:
        >>> AndroidUiElement.size
        {"heigth": int, "width": int}
    """
    def _get_default_ec(self) -> Set[ec]:
        return {ec.visibility_of_element_located}

    def _get_find_method(self) -> callable:
        if self.wait_type == "xpath":
            method = self.search_context.find_element_by_xpath
        else:
            method = self.search_context.find_element_by_android_uiautomator
        return method

    def tap(self) -> AndroidUiElement:
        self.logger.debug(f"Tap {self.wrapped_object} {self.selector}")
        self.wrapped_object.click()
        return self

    def __get_relative_elements_by_xpath(self, xpath) -> Union[AndroidUiElement, List[AndroidUiElement]]:
        return self.elements(xpath=xpath)

    def get_descendants(self) -> List[AndroidUiElement]:
        return self.__get_relative_elements_by_xpath("descendant::node()")[1:]

    def is_checked(self) -> bool:
        return eval(self.wrapped_object.get_attribute("checked").capitalize())

    def get_id(self) -> str:
        return self.wrapped_object.get_attribute("resource-id")

    def get_descr(self) -> str:
        return self.wrapped_object.get_attribute("content-desc")

    def get_cls_name(self) -> str:
        return self.wrapped_object.get_attribute("class")

    def get_text(self) -> str:
        return self.wrapped_object.text

    def elements(
            self,
            id_: Optional[str] = None,
            cls_name: Optional[str] = None,
            text: Optional[str] = None,
            text_contains: Optional[str] = None,
            descr: Optional[str] = None,
            descr_contains: Optional[str] = None,
            xpath: Optional[str] = None,
            do_stop_at_first_found: bool = False,
    ) -> List[AndroidUiElement]:
        """
        finds elements in this element's descendants
        does not scroll, therefore the target element must already be in view
        """

        if id_:
            selenium_elements = self.wrapped_object.find_elements_by_id(id_)
            return elements_factory(
                driver=self.driver,
                explicit_element=selenium_elements,
                search_context=self.wrapped_object,
            )

        if xpath:
            return elements_factory(
                driver=self.driver,
                search_context=self.wrapped_object,
                xpath=xpath
            )

        required_criteria = {
            k: v for k, v
            in locals().items()
            if k not in {"self", "id_", "do_stop_at_first_found"} and v is not None
        }

        if len(required_criteria) == 1 and "cls_name" in required_criteria:
            self.wait()
            selenium_elements = self.wrapped_object.find_elements_by_class_name(cls_name)
            return elements_factory(driver=self.driver, explicit_element=selenium_elements)

        descendants = self.get_descendants()
        elements = []

        for element in descendants:
            criteria_match_count = 0
            for rc_name, rc_value in required_criteria.items():
                if rc_name == "cls_name":
                    if element.get_cls_name() == rc_value:
                        criteria_match_count += 1
                elif rc_name == "text":
                    if element.get_text() == rc_value:
                        criteria_match_count += 1
                elif rc_name == "text_contains":
                    if rc_value in element.get_text():
                        criteria_match_count += 1
                elif rc_name == "descr":
                    if element.get_descr() == rc_value:
                        criteria_match_count += 1
                elif rc_name == "descr_contains":
                    if rc_value in element.get_descr():
                        criteria_match_count += 1
            if criteria_match_count >= len(required_criteria):
                if do_stop_at_first_found:
                    return [element]
                else:
                    elements.append(element)
        return elements

    def element(
            self,
            id_: Optional[str] = None,
            cls_name: Optional[str] = None,
            text: Optional[str] = None,
            text_contains: Optional[str] = None,
            descr: Optional[str] = None,
            descr_contains: Optional[str] = None,
            xpath: Optional[str] = None,
    ) -> AndroidUiElement:
        """
        finds the first element in this element's descendants that mes criteria or raises exception
        does not scroll, therefore the target element must already be in view
        """
        params = locals().copy()
        del params["self"]
        elements = self.elements(do_stop_at_first_found=True, **params)
        assert len(elements) <= 1
        if not elements:
            raise NoSuchElementException(pprint.pformat(params, indent=4))
        return elements[0]


class AndroidUiElementCollection(BaseAndroidElement):
    def _get_default_ec(self) -> Set[ec]:
        return set()

    def _get_find_method(self) -> callable:
        if self.wait_type == "xpath":
            method = self.search_context.find_elements_by_xpath
        else:
            method = self.search_context.find_elements_by_android_uiautomator
        return method

    def __iter__(self):
        return iter(self.wrapped_object)

    def __next__(self):
        return next(self.wrapped_object)

    def __len__(self):
        return len(self.wrapped_object)

    def __getitem__(self, item):
        return self.wrapped_object[item]
