import os

from behave import given, when, then

from lib import dashboard_lib as dl
from lib.device_control_lib import generate_random_imei
from lib.utils import parse_context_table_to_dict, check_csv_report
from dashboard.ImportPage import ImportPage
from dashboard.DevicesPage import DevicesPage
from dashboard.ReportPage import ReportPage
from config.config import get_csv_download_dir
from scripts.deleteIMEI import delete_imei


@given('a user belonging to MNO uploads a csv file to register using following contents')
@when('a user belonging to MNO uploads a csv file to register using following contents')
def step_impl(context):
    csv_file_content = parse_context_table_to_dict(context.table)
    for i in range(len(csv_file_content['imei'])):
        if 'random_imei' in csv_file_content['imei'][i]:
            csv_file_content['imei'][i] = generate_random_imei()
    if 'real_device_imei' in csv_file_content['imei']:
        csv_file_content['imei'] = context.imei
    dl.register_devices_with_csv(
        driver=context.driver,
        csv_file_content=csv_file_content,
    )
    context.csv_file_content = csv_file_content


@then('web UI shows the policy {policy} is applied on the device')
@when('web UI shows the policy {policy} is applied on the device')
@given('an enrolled device with "{policy}" policy via web UI')
def step_impl(context, policy):
    dl.assign_policy(context.driver, context.imei, policy)
    dl.wait_for_policy_applied_by_ui(context.driver, context.imei, policy)


@given('the file should be successfully uploaded into alps without any errors')
@then('the file should be successfully uploaded into alps without any errors')
def step_impl(context):
    context.import_page = ImportPage(context.driver)
    assert 'Upload complete' in context.import_page.get_upload_result_message()


@then("the user should be able to search for the uploaded imei's and view the device details")
def step_impl(context):
    devices_page = DevicesPage(context.driver)
    for imei in context.csv_file_content['imei']:
        devices_page.search_imei(imei)
        assert imei == devices_page.get_imei_from_summary()
    context.devices_page = devices_page


@then('the user should be able to view the following custom properties in device detail page')
def step_impl(context):
    custom_properties = parse_context_table_to_dict(context.table)
    device_properties = context.devices_page.get_device_properties()
    assert custom_properties == device_properties


@when('the "{policy}" assigned to the device')
@given('the "{policy}" assigned to the device')
def step_impl(context, policy):
    dl.assign_policy(context.driver, context.imei, policy)


@when('user exports CSV report with "{policy_name}" policy')
def step_impl(context, policy_name):
    report_page = ReportPage(context.driver)
    report_page.select_report_to_download(policy_name)
    report_page.download_csv_report(policy_name)


@then('exported CSV "{policy}" report file contains')
def step_impl(context, policy):
    expected_csv_content = parse_context_table_to_dict(context.table)
    csv_file_path = os.path.join(get_csv_download_dir(), "_" + policy + ".csv")
    if os.path.exists(csv_file_path):
        check_csv_report(expected_csv_content, csv_file_path)
    else:
        raise AssertionError("There is no {} file".format(csv_file_path))


@given('the device is not registered in the system')
def step_impl(context):
    delete_imei(imei=context.imei)
