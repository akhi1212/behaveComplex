from api.datastore_provision_controller_api import ProvisionControllerApi
from datetime import datetime
from time import time, sleep


def fetch_provision_records(imei, provisioning_type):
    """
    Find provisioning records

    :param imei: device`s imei
    :param provisioning_type: provisioning type used on device enrolment
    :return: response body
    """
    provision_api = ProvisionControllerApi()
    r = provision_api.fetch_provision_records(imei, provisioning_type)

    r.raise_for_status()
    r_data = r.json()
    return r_data


def kg_provisioning_action_time(imei, provisioning):
    """
    Find nextActionDueTime value from KnoxGuard Provisioning record

    :param imei: device`s imei
    :param provisioning: provisioning type used on device enrolment
    :return: nextActionDueTime value from KnoxGuard Provisioning record
    """
    r = fetch_provision_records(imei, provisioning)
    action_time_unix = r['records'][0]['provisioningModel']['knoxGuardProvisioning']['nextActionDueTime']
    action_time_converted = datetime.utcfromtimestamp(action_time_unix).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.strptime(action_time_converted, "%Y-%m-%d %H:%M:%S")


def wait_for_kg_status_job(imei, provisioning, param, expected_value=None, timeout=240):
    """
    Wait for Knox Guard status job work

    :param imei: device`s imei
    :param provisioning: provisioning type used on device enrolment
    :param param: requested parameter
    :param timeout: time to wait for a condition
    """
    period = 1
    start = time()

    while time() - start < timeout:
        record = fetch_provision_records(imei, provisioning)
        param_value = record['records'][0]['provisioningModel']['knoxGuardProvisioning'][param]
        if expected_value is not None:
            if param_value == expected_value:
                return True
        else:
            if param_value is not None:
                return True
        sleep(period)


def value_from_provisioning(imei, provisioning, param):
    """
    Return value of specified parameter from KnoxGuard Provisioning record

    :param imei: device`s imei
    :param provisioning: provisioning type used on device enrolment
    :param param: requested parameter
    :return: value for requested parameter from KnoxGuard Provisioning record
    """
    r = fetch_provision_records(imei, provisioning)
    value = r['records'][0]['provisioningModel']['knoxGuardProvisioning'][param]
    return value
