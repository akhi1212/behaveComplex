import logging
import os

from behave.runner import Context

from lib.utils import get_classes_from_dir
from device_ui.adb_controller.adb_controller import DeviceInfo
from device_ui.device_controller.settings.base_settings_android import SettingsAndroid, BaseSettingsAndroid

from config.config import config


logger = logging.getLogger(config.LOGGER_NAME + f".{__name__}.__init__")


def get_settings_instance(context: Context, device) -> SettingsAndroid:
    device_info: DeviceInfo = context.adb.get_device_info()
    make = device_info.manufacturer
    android_v = device_info.android_version

    path = os.path.dirname(__file__)
    settings_classes = get_classes_from_dir(class_type=BaseSettingsAndroid, path=path)

    for settings_class in settings_classes:
        if settings_class.manufacturer == make:  # noqa
            if settings_class.android_version == android_v:  # noqa
                return settings_class(device=device)
    logger.warning(f"No specific settings were found for {make} Android {android_v}.\n"
                   f"Using {BaseSettingsAndroid.__class__.__name__} instead.")
    return BaseSettingsAndroid(device=device)
