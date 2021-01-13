import logging
import sys

from device_ui import DeviceController, AdbController


logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

logger.setLevel(logging.DEBUG)


class MockBehaveContext:
    ...


context = MockBehaveContext()
context.adb = AdbController()
context.device = DeviceController(context=context, do_press_home=True)  # noqa

bt = "Bluetooth"
assert context.device.settings.open(bt).toggle_switch(bt, False).toggle_switch(bt, True).is_switch_on(bt)

fsn = "Force activities to be resizable"
context.device.settings.open().tap_menu("System").tap_menu("Developer options").toggle_switch(fsn, True).toggle_switch(fsn, False)
assert not context.device.settings.is_switch_on(fsn)

context.device.press_button("home").press_button("recent_apps")

assert context.device.security_app.home_screen.is_open()  # just an example of how we'll access screen methods

context.device.disconnect()
