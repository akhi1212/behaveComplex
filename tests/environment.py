import functools
import os
import logging
import traceback

from behave import fixture, use_fixture
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import selenium.webdriver.firefox.options as firefox_options
import selenium.webdriver.chrome.options as chrome_options

from device_ui import DeviceController, AdbController
from config.config import config
from config.config import get_csv_download_dir
from lib.admin_control_lib import setup_admin_record, generate_tac_entity, update_admin_record
from lib.policy_control_lib import update_policy_record, setup_test_policies
from lib.device_control_lib import register_device, generate_random_imei
from lib.log import configure_logging
from lib.utils import run_in_command_line, empty_download_folder, get_timestamp
from scripts.deleteIMEI import delete_imei


logger = logging.getLogger(config.LOGGER_NAME + ".environment.py")


def fixture_with_traceback(fixture_) -> callable:
    @functools.wraps(fixture_)
    def wrapped_fixture(*a, **kw):
        try:
            actual_fixture = fixture(fixture_)
            result = use_fixture(actual_fixture, *a, **kw)
        except BaseException:
            trb = traceback.format_exc()
            logger.exception(trb)
            raise
        else:
            return result
    return fixture(func=wrapped_fixture, name=fixture_.__name__ + "_with_traceback")


def before_all(context):
    loglevel = context.config.userdata.get("loglevel", config.log_level)
    configure_logging(loglevel, config.log_to_file)
    logger.info('[Test run Setup]')
    context.env = use_fixture(environment_setup, context)


def before_feature(context, feature):
    logger.info('[Feature Setup]')
    if 'E2E_Tests' in feature.tags:
        context.imei = config.real_device_imei
        context.provisioning = 'KNOX_GUARD' if 'KNOX_GUARD' in feature.tags else 'ALPS'
        update_admin_record(tac_entity=generate_tac_entity(context.imei, provisioning=context.provisioning))


def after_all(context):
    logger.info('[Test run Teardown]')
    if hasattr(context, 'ssh_tunnel'):
        context.ssh_tunnel.kill()
    empty_download_folder()


def before_tag(context, tag):
    if tag.startswith("fixture.policy:"):
        use_fixture(create_update_policy, context, tag.split(':')[-1])
    elif tag.startswith("fixture.new_device_with_provisioning:"):
        provisioning = tag.split(':')[-1]
        use_fixture(create_device, context, 'TEST_SHIPPED', provisioning)


def before_scenario(context, scenario):
    logger.info(f'[Scenario Setup][{scenario.name}]')
    if 'skip' in scenario.tags or \
            True in [('env:' in tag and context.env != tag.split(':')[-1]) for tag in scenario.tags]:
        scenario.skip(f'Scenario: {scenario.name} - skipped')
    if context.active_outline:
        outline = context.active_outline
        if 'imei' in outline.headings:
            imei = outline.cells[outline.headings.index('imei')]
            logger.info(f'Enrolling new imei {imei}')
            provisioning = outline.cells[outline.headings.index('provisioning')]
            policy = outline.cells[outline.headings.index('policy')]
            use_fixture(create_device, context, policy, provisioning, imei)
    if 'E2E_Tests' in scenario.feature.tags:
        browser = context.config.userdata.get("browser", "chrome")
        logger.info(f'[{browser.upper()} browser Setup]')
        if browser == "firefox":
            use_fixture(browser_firefox, context)
        elif browser == "chrome":
            use_fixture(browser_chrome, context)
        else:
            raise Exception(f"There is no support for driver: {browser}")
        if "no_device" not in scenario.tags:
            logger.info("Connect to ADB")
            context.adb = AdbController()
            use_fixture(appium, context)


def after_scenario(context, scenario):
    logger.info(f'[Scenario Teardown][{scenario.name}]')
    update_admin_record()  # teardown of admin record
    setup_test_policies()
    if hasattr(context, 'imei') and context.env in ['test4_qa', 'test5_qa'] and 'E2E_Tests' not in scenario.feature.tags:
        delete_imei(context.imei)


def after_step(context, step):
    if step.status.name == "failed":
        logger.error(F"Step failed: {step.name}")
        if 'E2E_Tests' in context.scenario.feature.tags and "no_device" not in context.scenario.tags:
            use_fixture(save_device_screenshot, context)


@fixture_with_traceback
def environment_setup(context):
    env = context.config.userdata.get("environment", "local")
    config.re_init_for_env(env)
    if env in ['test4_qa', 'test5_qa']:
        context.ssh_tunnel = run_in_command_line(config.ssh_forw_cmd.split(), need_output=False)
        context.days_to_minutes = False
    else:
        context.days_to_minutes = True
    logger.info(f'ENV: {env}')
    logger.info('Setting up test policies')
    setup_test_policies()
    logger.info('Setting up admin record')
    setup_admin_record()
    return env


@fixture_with_traceback
def create_update_policy(context, policy):
    context.policy = policy
    yield update_policy_record(policy=policy)


@fixture_with_traceback
def create_device(context, policy, provisioning, imei=None, custom_properties=None):
    if not imei or 'random' in imei:
        imei = generate_random_imei(provisioning)
    else:
        update_admin_record(tac_entity=generate_tac_entity(imei, provisioning))
    logger.info(f'Registering new IMEI: {imei}')
    register_device(imei, policy, custom_properties)
    context.imei = imei
    context.policy = policy
    context.provisioning = provisioning


@fixture_with_traceback
def browser_firefox(context):
    try:
        profile = webdriver.FirefoxProfile()
        options = firefox_options.Options()
        profile.set_preference('browser.download.folderList', 2)  # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference("browser.download.dir", get_csv_download_dir())
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("browser.download.manager.useWindow", False)
        profile.set_preference("browser.download.manager.focusWhenStarting", False)
        profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
        profile.set_preference("browser.download.manager.showAlertOnComplete", False)
        profile.set_preference("browser.download.manager.closeWhenDone", False)
        profile.set_preference("pdfjs.disabled", True)

        options.headless = config.web_ui_headless
        context.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options,
                                           firefox_profile=profile)
        yield context.driver
    finally:
        context.driver.quit()


@fixture_with_traceback
def browser_chrome(context):
    try:
        options = chrome_options.Options()
        prefs = {"profile.default_content_setting_values.automatic_downloads": 2,
                 "download.default_directory": get_csv_download_dir(),
                 "download.prompt_for_download": False,
                 "safebrowsing.enabled": True,
                 "directory_upgrade": True}
        options.add_experimental_option("prefs", prefs)
        options.headless = config.web_ui_headless

        context.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        yield context.driver
    finally:
        context.driver.quit()


@fixture_with_traceback
def appium(context):
    logger.info("Connect to Appium")
    context.device = DeviceController(context=context)
    context.device_serialno = context.device.info.serial_number
    context.imei = context.device.info.imei
    yield
    context.device.disconnect()


@fixture_with_traceback
def save_device_screenshot(context):
    screenshot_name = get_timestamp() + ".png"
    os.makedirs(config.SCREENSHOT_PATH, exist_ok=True)
    destination = os.path.join(config.SCREENSHOT_PATH, screenshot_name)
    context.device.save_screenshot(dest=destination)
