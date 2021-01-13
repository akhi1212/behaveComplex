WAIT_TIMEOUT = 10

DESIRED_CAPABILITIES = {
    "platformName": "Android",
    "platformVersion": str,
    "automationName": "uiautomator2",
    "newCommandTimeout": 60 * 60,
}

APPIUM_HOST = "127.0.0.1"
APPIUM_PORT = "4723"
APPIUM_ADDRESS = "http://{host}:{port}/wd/hub".format(host=APPIUM_HOST, port=APPIUM_PORT)
