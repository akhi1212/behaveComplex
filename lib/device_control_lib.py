import logging
import copy
import random
import time
import uuid
import polling
import requests

from api.admin_api import DeviceRestController
from api.datastore_device_controller_api import DeviceControllerApi
from api.device_service_api import DeviceServiceApi
from api.public_api import PublicAPI
from config.config import config
from resources.data_models import DS_ENROL_JSON, ADMIN_SAMPLE_JSON, DS_CHECKIN_JSON


logger = logging.getLogger(config.LOGGER_NAME + f".{__name__}")


def register_device(imei: str, policy: str, custom_properties=None, jwt_token: str = None, ignore_errors: bool = False):
    """
    Register new imei via Public API

    :param imei: device`s imei
    :param policy: policy name to enrol with
    :param custom_properties: dictionary with custom properties
    :param jwt_token: JWT token (optional)
    :param ignore_errors: True in case response status code verification should be ignored and False in other case
    :return: response body
    """
    public_api = PublicAPI()
    r = public_api.register_device([{"assignedPolicy": policy,
                                     "imei": imei,
                                     "customProperties": custom_properties}],
                                   authorization_header=jwt_token)
    r_data = r.json()
    if not ignore_errors:
        r.raise_for_status()
        if 'error' in r_data['devices'][0].keys():
            if r_data['devices'][0]['error']['code'] == 'IMEI_ALREADY_REGISTERED':
                logger.warning(f'IMEI {imei} is already registered')
            else:
                logger.exception(f'Error on device registering with IMEI {imei}: {r_data["devices"][0]["error"]}')
    return r_data


def register_devices(devices: list, jwt_token: str = None):
    """
    Register new imei of several devices via Public API

    :param devices: a list of dicts each containing imei, assignedPolicy and customProperties values.
                   Example: [{"imei": "359039083459002", "assignedPolicy": "TEST_SHIPPED",
                              "customProperties": {"property1": "abc"}},
                             {"imei": "354267096922650", "assignedPolicy": "TEST_LOCK",
                              "customProperties": {"property1": "qwe"}}]
    :param jwt_token: JWT token (optional)
    """
    public_api = PublicAPI()
    r = public_api.register_device(devices, authorization_header=jwt_token)
    r.raise_for_status()
    r_data = r.json()
    for r_device_data in r_data['devices']:
        if 'error' in r_device_data.keys():
            if r_device_data['error']['code'] == 'IMEI_ALREADY_REGISTERED':
                logger.warning(f"IMEI {r_device_data['imei']} is already registered")
            else:
                logger.exception(f"Error on device registering with IMEI {r_device_data['imei']}: "
                                 f"{r_device_data['error']}")
    return r_data


def update_device(imei: str, policy: str, custom_properties=None, force_reapply=False, ignore_errors=False,
                  jwt_token: str = None):
    """
    Update device via Public API
    :param imei: device`s imei
    :param policy: policy name
    :param custom_properties: dictionary with custom properties
    :param force_reapply: if True, cause the assigned policy to be treated as newly applied
    :param ignore_errors: if True, return response body despite errors
    :param jwt_token: JWT token (optional)
    :return: response body
    """
    public_api = PublicAPI()
    r = public_api.update_device([{"assignedPolicy": policy,
                                   "imei": imei,
                                   "customProperties": custom_properties,
                                   "forceReapply": force_reapply}],
                                 authorization_header=jwt_token)
    r_data = r.json()
    if not ignore_errors:
        r.raise_for_status()
        assert 'error' not in r_data['devices'][0].keys(), \
            logger.exception(f'Error updating {imei}: {r_data["devices"][0]["error"]}')
    return r_data


def update_devices(devices: list, ignore_errors: bool = False, jwt_token: str = None):
    """
    Update device via Public API

    :param devices: a list of dicts each containing imei, assignedPolicy, customProperties and forceReapply values
                    Example: [{"imei": "359039083459002", "assignedPolicy": "TEST_SHIPPED",
                              "customProperties": {"property1": "abc"}, "forceReapply": True},
                             {"imei": "354267096922650", "assignedPolicy": "TEST_LOCK",
                              "customProperties": {"property1": "qwe"}, "forceReapply": True}]
    :param ignore_errors: if True, return response body despite errors
    :param jwt_token: JWT token (optional)
    :return: response body
    """
    public_api = PublicAPI()
    r = public_api.update_device(devices, authorization_header=jwt_token)
    r_data = r.json()
    if not ignore_errors:
        r.raise_for_status()
        for r_device_data in r_data['devices']:
            if 'error' in r_device_data.keys():
                logger.exception(f'Error updating {r_device_data["imei"]}: {r_device_data["error"]}')
        assert not [r_device_data for r_device_data in r_data['devices'] if 'error' in r_device_data.keys()]
    return r_data


def get_device_status(imei: str, jwt_token: str = None, ignore_errors: bool = False):
    """
    Fetch device status via Public API

    :param imei: device`s imei
    :param jwt_token: JWT token (optional)
    :param ignore_errors: True in case response status code verification should be ignored and False in other case
    :return: response body
    """
    public_api = PublicAPI()
    r = public_api.get_status_of_the_device(imei, authorization_header=jwt_token)
    if not ignore_errors:
        r.raise_for_status()
    return r.json()


def generate_random_imei(provisioning='ALPS'):
    """
    Returns randomly generated imei based on tac for specific provisioning type

    :param provisioning: provisioning type
    :return: imei
    """
    imei = config.test_tacs[provisioning] + ''.join(str(random.randrange(0, 9)) for _ in range(7)) \
        if provisioning else ''.join(str(random.randrange(0, 9)) for _ in range(15))
    return imei


def enrol_device_with_file(file_path):
    """
    Upload new device via Admin API with csv file

    :param file_path: absolute path to csv file
    :return: response body
    """
    device_controller = DeviceRestController()
    r = device_controller.device_enrolment(file_path=file_path)
    r.raise_for_status()
    r_data = r.json()
    return r_data


def get_device_record(imei: str):
    """
    Get a device record from Datastore

    :param imei: device`s imei
    :return: record data
    """
    device_controller = DeviceControllerApi()
    r = device_controller.get_device_record(imei=imei)
    r.raise_for_status()
    r_data = r.json()
    return r_data


def post_enrol(enrol_json: dict):
    """
    Send enrol request to Device Service

    :param enrol_json: dictionary with enrol data
    :return: response body
    """
    device_service_api = DeviceServiceApi()
    r = device_service_api.post_enrol(enrol_json=enrol_json)
    r.raise_for_status()
    r_data = r.json()
    if 'error' in r_data.keys():
        logger.exception(f'Error on device registering: {r_data["error"]}')
    return r_data


def get_enrol_token(imei: str, provision_type: str):
    """
    Returns enrol token

    :param imei: device`s imei
    :param provision_type: provisioning type: "ALPS" or "KNOX_GUARD"
    :return: token string
    """
    enrol_json = DS_ENROL_JSON
    enrol_json = copy.deepcopy(enrol_json)
    enrol_json["core"]["imei"] = imei
    enrol_json["core"]["serial"] = config.SERIAL_TEST
    enrol_json["core"]["owner"] = config.owner
    enrol_json["publicKey"] = ADMIN_SAMPLE_JSON["model"]["publicKey"]
    enrol_json["core"]["challengeSeed"] = str(uuid.uuid4().hex)
    enrol_json["core"]["provisioned"] = provision_type

    response = post_enrol(enrol_json)
    token = response["token"]
    return token


def fill_checkin_values(current_policy: str, transition_policy: str, checkin_json: dict, activate_policy=False):
    """
    Generates json like data for checkin request

    :param current_policy: current policy name
    :param transition_policy: transition policy name
    :param checkin_json: data model of checkin body that will be updated and returned
    :param activate_policy: if True, sets currentPolicyActivatedTime time
    :return: checkin_json with updated fields
    """
    checkin_json["currentStatus"]["currentPolicyId"] = config.owner + '/' + current_policy
    checkin_json["currentStatus"]["transitionPolicyId"] = config.owner + '/' + transition_policy \
        if transition_policy else None

    time_now = int(time.time())
    checkin_json["currentStatus"]["deviceLastCheckin"] = time_now
    checkin_json["currentStatus"]["deviceNextCheckin"] = time_now + 10  # 10 seconds delay
    checkin_json["currentStatus"]["currentPolicyVersion"] += 1
    checkin_json["currentStatus"]["transitionPolicyVersion"] += 1
    if activate_policy:
        checkin_json["currentStatus"]["currentPolicyActivatedTime"] = time_now + 11
    return checkin_json


def post_checkin(imei, provision_type, current_policy, transition_policy=None, enable_activation=False):
    """
    Send checkin request to Device Service

    :param imei: device`s imei
    :param provision_type: provisioning type: "ALPS" or "KNOX_GUARD"
    :param current_policy: current policy name
    :param transition_policy: transition policy name
    :param enable_activation: enables policy activation in case of using "KNOX_GUARD" provisioning type
    :return: response body
    """
    device_service_api = DeviceServiceApi()
    token = get_enrol_token(imei, provision_type)

    checkin_json = copy.deepcopy(DS_CHECKIN_JSON)
    checkin_json = fill_checkin_values(current_policy, transition_policy, checkin_json,
                                       activate_policy=enable_activation)
    r = device_service_api.post_checkin(checkin_json, authorization_header=token)
    return r.json()


def wait_for_policy_applied_by_api(imei, policy, timeout=180):
    """
    Wait for policy applied

    :param imei: device`s imei
    :param policy: required policy
    :param timeout: time to wait for a condition
    """

    polling.poll(
        target=lambda:
            (get_device_record(imei))['model']['status']['currentPolicyId']
            ==
            config.owner + '/' + policy,
        step=2,
        timeout=timeout,
        ignore_exceptions=(requests.exceptions.HTTPError,),
    )
