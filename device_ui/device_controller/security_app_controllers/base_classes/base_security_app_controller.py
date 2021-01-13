# import logging
from abc import ABC, abstractmethod
from typing import TypeVar

# from config.config import config
from device_ui.device_controller.security_app_controllers.base_classes.base_android_screen import BaseAndroidScreen


class BaseSecurityAppUiController(BaseAndroidScreen, ABC):
    # def __init__(self, device):
    #     from device_ui.device_controller.device_controller import DeviceController
    #     self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
    #     self.device: DeviceController = device

    def __repr__(self):
        return self.__class__.__name__

    @abstractmethod
    def is_screen_locked(self) -> bool:
        """
        Tells if the device is locked by the security app
        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        """
        Starts ALPS or KnoxGuard
        """
        raise NotImplementedError


SecurityAppController = TypeVar("SecurityAppController", bound=BaseSecurityAppUiController)
