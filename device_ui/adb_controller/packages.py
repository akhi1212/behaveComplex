"""
See use example in BaseSettingsAndroid.open
>>> from device_ui.device_controller.settings.base_settings_android import BaseSettingsAndroid
>>> BaseSettingsAndroid.open
"""

from typing import Dict


class MetaPackage(type):
    def __new__(mcs, *args, **kwargs):
        assert isinstance(args[2]["name"], str), f'{args[0]} class attribute "name" must be a string'
        assert isinstance(args[2]["activities"], dict), f'{args[0]} class attribute "activities" must be a dict'
        return super().__new__(mcs, *args, **kwargs)


class BasePackage(metaclass=MetaPackage):
    name: str = ""
    activities: Dict[str, str] = {}


class HuaweiAndroid9SettingsPackage(BasePackage):
    name = "com.android.settings"
    activities = {
        "Settings": "com.android.settings.HWSettings",
        "Bluetooth": "com.android.settings.bluetooth.BluetoothSettings",
        "Language and region": "com.android.settings.Settings$LocalePickerActivity",
        "Info": "android.settings.APPLICATION_DETAILS_SETTINGS",
    }


class AlpsPackage(BasePackage):
    name = "com.trustonic.telecoms.standard.dpc"
    activities = {
        "Main": "com.trustonic.alps.alpsclientservice.lock.MainActivity",
    }


PACKAGES = {
    "HUAWEI": {
        "9":  {
            "Settings": HuaweiAndroid9SettingsPackage,
        }
    },

    "ALPS": AlpsPackage,

}
