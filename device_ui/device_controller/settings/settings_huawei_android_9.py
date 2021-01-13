import re
from typing import List, Union

import polling
from selenium.common.exceptions import NoSuchElementException

from device_ui.constants.languages import lang_map, Language
from device_ui.device_controller.settings.base_settings_android import BaseSettingsAndroid, SettingsAndroid
from device_ui.device_controller.ui_elements.android_element import AndroidUiElement
from device_ui.constants.android_ui_constants import SETTINGS as SC


class SettingsHuaweiAndroid9(BaseSettingsAndroid):
    manufacturer = "HUAWEI"
    android_version = "9"

    def get_installed_languages(self, return_elements: bool = False) -> Union[List[AndroidUiElement], List[str]]:
        """
        :param return_elements: True => return  List[AndroidUiElement]; False => return List[str]
        :return: Either a list of widgets, one for each language, or a list of language names
        """
        recycler = self.element(cls_name=SC.RECYCLER.value)
        descendants = recycler.get_descendants()
        languages = []
        for element in descendants:
            description = element.get_descr() or ""
            if re.match(r"\d{1,2}, \w+", description):
                if return_elements:
                    languages.append(element)
                else:
                    text = element.element(id_=SC.LABEL.value).get_text()
                    languages.append(text)
        self.logger.debug(f"Installed languages: {languages}")
        return languages

    def add_language(self, lang_shortname: str, do_change_lang: bool = True) -> SettingsAndroid:
        """
        Install a language
        :param lang_shortname: e.g. "es"
        :param do_change_lang: switch to the installed language
        """
        language: Language = lang_map[lang_shortname]
        if language.native_name not in self.get_installed_languages():
            self.logger.info(f"Add language {language.eng_name}")
            self.element(id_=SC.ADD_LANG.value).tap()
            self.element(id_=SC.SEARCH_INPUT.value, do_scroll=False).set_text(language.eng_name)
            lang_list = self.elements(descr_contains=language.eng_name)
            lang_list = [el for el in lang_list if language.native_name in el.get_text().split("\n")]
            assert len(lang_list) == 1, f'{len(lang_list)} languages for search "{language.eng_name}" were found'
            lang_list[0].tap()
            if do_change_lang:
                self.element(id_=SC.BUTTON_1.value).tap()
            else:
                self.element(id_=SC.BUTTON_2.value).tap()
            assert language.native_name in self.get_installed_languages()
        return self

    def _get_language_button(self, language) -> AndroidUiElement:
        """
        On the screen "Language and region finds the widget that corresponds to language
        :param language: Language name as it's shown on the screen in bold font
        :return: the widget that corresponds to language
        """
        installed_languages = self.get_installed_languages(return_elements=True)
        for element in installed_languages:
            if element.element(id_=SC.LABEL.value).get_text() == language:
                return element
        raise NoSuchElementException(f"Language {language} is not installed")

    def set_language(self, lang_shortname: str) -> SettingsAndroid:
        """
        First, adds the language if it's not installed. Then, sets it
        :param lang_shortname: e.g. "en"
        """
        lang, country = self.device.get_locale()
        if lang != lang_shortname:
            language: Language = lang_map[lang_shortname]
            self.logger.info(f"Set language to {language.native_name}")
            self.add_language(lang_shortname=lang_shortname)
            self._get_language_button(language=language.native_name).tap()
            polling.poll(target=lambda: self.device.get_locale() == (lang_shortname, country), step=2, timeout=10)
        return self

    def get_region(self) -> str:
        region = self.element(id_=SC.REGION_CURRENT.value).get_text()
        self.logger.debug(f"Current region: {region}")
        return region

    def set_region(self, region: str) -> SettingsAndroid:
        current_region = self.get_region().strip()
        if current_region != region:
            self.logger.info(f"Set region to {region}")
            self.element(id_=SC.BUTTON_REGION.value).tap()
            self.element(id_=SC.SEARCH_INPUT.value, do_scroll=False).set_text(region)
            self.elements(text=region)[-1].tap()
            polling.poll(target=lambda: self.get_region() == region, step=2, timeout=10)
        return self
