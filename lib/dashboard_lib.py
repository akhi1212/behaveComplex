import polling
import requests

from dashboard.ImportPage import ImportPage
from lib import device_control_lib as dcl
from dashboard.DevicesPage import DevicesPage
from lib.utils import make_enrol_device_file


def register_devices_with_csv(driver, csv_file_content: dict):
    """
    Register devices via uploading csv file on Import from Dashboard UI

    :param driver: webdriver instance
    :param csv_file_content: dictionary with structure
                            {'imei': [<imei1>, <imei2>], 'policy': [<policy1>, '<policy2>],
                            'custom_property1': [<value1>, <value2>]}
    :return: None
    """
    csv_file_path = make_enrol_device_file(csv_file_content)
    import_page = ImportPage(driver)
    import_page.login()
    import_page.register(csv_file_path)
    if "policy" in csv_file_content:
        dcl.wait_for_policy_applied_by_api(imei=csv_file_content["imei"], policy=csv_file_content["policy"])


def assign_policy(driver, imei, policy):
    devices_page = DevicesPage(driver)
    import_page = ImportPage(driver)
    if not import_page.check_dashboard_is_opened():
        import_page.login()
    if not devices_page.is_device_page_opened():
        devices_page.search_imei(imei)
    if imei not in devices_page.get_imei_from_summary():
        devices_page.search_imei(imei)
    if devices_page.get_current_policy() != policy:
        devices_page.assign_policy(policy, imei)


def wait_for_policy_applied_by_ui(driver, imei, policy, timeout=180):
    """
    Wait for policy applied

    :param driver: webdriver instance
    :param imei: device`s imei
    :param policy: required policy
    :param timeout: time to wait for a condition
    """
    devices_page = DevicesPage(driver)
    if imei not in devices_page.get_imei_from_summary():
        devices_page.search_imei(imei)

    polling.poll(
        target=lambda:
            devices_page.get_current_policy(do_refresh=True) == policy,
        step=2,
        timeout=timeout,
        ignore_exceptions=(requests.exceptions.HTTPError,),
    )
