import copy
import random
import datetime
import operator

from functools import reduce as reduce
from api.datastore_policy_controller_api import PolicyControllerApi
from api.public_api import PublicAPI
from lib.device_control_lib import get_enrol_token
from config.config import config
from resources.data_models import POLICY_SAMPLE_JSON
from resources.test_policies import *

test_policies = {'TEST_SHIPPED': TEST_SHIPPED,
                 'TEST_LOCK': TEST_LOCK,
                 'TEST_UNLOCK': TEST_UNLOCK,
                 'TEST_MESSAGE': TEST_MESSAGE,
                 'TEST_NOTIFICATION': TEST_NOTIFICATION,
                 'TEST_BLINK': TEST_BLINK,
                 'TEST_RELEASE': TEST_RELEASE}

policy_name_from_type = {
    "LOCK": "TEST_LOCK",
    "MESSAGE": "TEST_MESSAGE",
    "NOTIFICATION": "TEST_NOTIFICATION"
}

message_path_in_policy_record = {
    "ALPS": {
        "TEST_LOCK": (
            'policyModel', 'definition', 'definitionV1', 'deviceLock', 'screenLock', 'message', 'defaultValue'),
        "TEST_UNLOCK": ('policyModel', 'definition', 'definitionV1', 'notification', 'defaultValue'),
        "TEST_MESSAGE": ('policyModel', 'definition', 'definitionV1', 'notification', 'defaultValue'),
        "TEST_NOTIFICATION": ('policyModel', 'definition', 'definitionV1', 'notification', 'defaultValue')
    },
    "KNOX_GUARD": {
        "TEST_LOCK": ('policyModel', 'definition', 'definitionV1', 'knoxGuardScreenLock', 'message'),
        "TEST_UNLOCK": ('policyModel', 'definition', 'definitionV1', 'knoxGuardMessage', 'message'),
        "TEST_MESSAGE": ('policyModel', 'definition', 'definitionV1', 'knoxGuardMessage', 'message'),
        "TEST_BLINK": ('policyModel', 'definition', 'definitionV1', 'knoxGuardDismissibleScreenLock', 'message')
    }
}


def get_from_dict(root: dict, items: iter):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_in_dict(root: dict, items: iter, value: str):
    """Set a value in a nested object in root by item sequence."""
    reduce(operator.getitem, items[:-1], root)[items[-1]] = value
    return root


def update_policy_record(policy: str, policy_record=None):
    """
    Update policy configuration on server

    :param policy: policy name
    :param policy_record: policy data in dictionary form,
    if None will get default policy settings by policy name from test_policies scope
    :return: response body
    """
    policy_api = PolicyControllerApi()

    record = policy_record if policy_record else get_policy_record(policy)
    record["id"] = record["policyModel"]["reference"]["id"] = config.owner + '/' + policy

    r = policy_api.update_single_record(record)
    r.raise_for_status()
    return r


def setup_test_policies():
    """
    Setup all test policies on server

    :return: None
    """
    for policy in test_policies:
        update_policy_record(policy)


def generate_pin(imei: str, provisioning: str, jwt_token: str = None, ignore_errors: bool = False):
    """
    Generate pin via Public API

    :param imei: device`s imei
    :param provisioning: provisioning type used on device enrolment
    :param jwt_token: JWT token (optional)
    :param ignore_errors: True in case response status code verification should be ignored and False in other case
    :return: response body
    """
    if provisioning == "ALPS":
        get_enrol_token(imei, provisioning)

    public_api = PublicAPI()
    r = public_api.get_pin(imei=imei, challenge=str(random.randint(0, 999999)), authorization_header=jwt_token)
    if not ignore_errors:
        r.raise_for_status()
    pin_response = r.json()
    return pin_response


def get_policy_record(policy_id=None, from_server=False):
    """
    Returns policy data model by name

    :param policy_id: policy id without owner. If None - returns policy sample json
    :param from_server: if True will fetch policy record from server else will get from test_policies dictionary
    :return: policy data model
    """
    if not from_server:
        res = copy.deepcopy(test_policies[policy_id] if policy_id in test_policies.keys() else POLICY_SAMPLE_JSON)
    else:
        policy_api = PolicyControllerApi()
        r = policy_api.get_single_record(config.owner + '/' + policy_id)
        r.raise_for_status()
        res = r.json()['records'][0]
    return res


def configure_delayed_activation(policy, start_time=None, end_time=None, days=None, exclude_holidays=False,
                                 once_per_day=False, repetition_interval=None, non_dismissible=False,
                                 activation_duration=None):
    """
    Returns policy record with configured delayed activation

    :param policy: policy name
    :param start_time: start time timestamp
    :param end_time: end time timestamp
    :param days: list of days names; if days = 'All' will take all days
    :param exclude_holidays: exclude holidays option
    :param once_per_day:  once per day option
    :param repetition_interval: repetition interval in seconds
    :param non_dismissible: non dismissible option
    :param activation_duration: activation duration in seconds
    :return: policy record
    """
    policy_record = get_policy_record(policy)
    policy_definition = policy_record['policyModel']['definition']['definitionV1']
    for schedule in 'alpsActionScheduling', 'kgActionScheduling':
        policy_definition[schedule] = {}
        policy_definition[schedule]['delayInitialActivation'] = True
        policy_definition[schedule]['activationWindow'] = {}
        policy_definition[schedule]['activationWindow']['start'] = start_time if start_time else 55555
        policy_definition[schedule]['activationWindow']['end'] = end_time if end_time else 77777
        policy_definition[schedule]['activationWindow']['days'] = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY",
                                                                   "FRIDAY", "SATURDAY",
                                                                   "SUNDAY"] if days == 'All' else days
        policy_definition[schedule]['activationWindow']['excludeHolidays'] = exclude_holidays
        policy_definition[schedule]['nonDismissible'] = non_dismissible
        policy_definition[schedule]['oncePerDay'] = once_per_day
        policy_definition[schedule]['activationDuration'] = activation_duration
        policy_definition[schedule]['repetitionInterval'] = repetition_interval

    return policy_record


def configure_automated_transition(policy: str, reference_policy: str, days, from_state='ASSIGNED', days_active=None,
                                   exclude_holidays=False, days_to_minutes=True):
    """
    Returns policy record with configured automated transition

    :param policy: policy name
    :param reference_policy: transition policy name
    :param days: number of days
    :param from_state: from "ASSIGNED" or "ACTIVATED"
    :param days_active: by default will take all days; 'except tomorrow' - all days except tomorrow
    :param exclude_holidays: True if exclude_holidays == 'Checked' else False
    :param days_to_minutes: if True will set 'days' to [current minutes] + [days]
    :return: policy record
    """
    policy_record = get_policy_record(policy)
    policy_definition = policy_record['policyModel']['definition']['definitionV1']
    policy_transition = policy_definition['serverScheduledTransition'] = {}
    policy_transition['reference'] = {
        "id": config.owner + '/' + reference_policy,
        "version": None,
        "assignedTime": 0,
        "tags": {}
    }
    policy_transition['days'] = int(days) if not days_to_minutes else datetime.datetime.now().minute + int(days)
    policy_transition['from'] = from_state

    week_days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    if days_active == 'except tomorrow':
        del week_days[datetime.datetime.today().weekday() + 1]
    elif days_active == 'today':
        week_days = [week_days[datetime.datetime.today().weekday()]]

    policy_transition['window'] = {'days': week_days,
                                   'excludeHolidays': True if exclude_holidays == 'Checked' else False}

    return policy_record


def remove_transition_settings(policy, from_server=True):
    """
    Removing automated transition from policy record

    :param policy: policy name
    :param from_server: if True will fetch policy record from server else will get from test_policies dictionary
    :return: policy record
    """
    policy_record = get_policy_record(policy, from_server=from_server)
    policy_record['policyModel']['definition']['definitionV1']['serverScheduledTransition'] = None
    return policy_record


def update_lock_policy_w_localized_text(policy, localised_title, localised_msg, locale, from_server=True):
    """
    Returns lock policy record with configured localised title and messages

    :param policy: policy name
    :param localised_title: localised text for title
    :param localised_msg: localised text for message
    :param locale: 2 Letter Language code
    :param from_server: if True will fetch policy record from server else will get from test_policies dictionary
    :return: policy record
    """
    policy_record = get_policy_record(policy, from_server=from_server)
    policy_record['policyModel']['definition']['definitionV1']['deviceLock']['screenLock']['title'][
        'localeValues'][locale] = localised_title
    policy_record['policyModel']['definition']['definitionV1']['deviceLock']['screenLock']['message'][
        'localeValues'][locale] = localised_msg
    return policy_record


def get_actual_message(policy, provisioning, from_server=True):
    """
    Returns message value for required policy from policy record on server

    :param policy: policy name
    :param provisioning: device provisioning type
    :param from_server: if True will fetch policy record from server else will get from test_policies dictionary
    :return: default message value for required policy
    """
    return get_from_dict(get_policy_record(policy, from_server=from_server), message_path_in_policy_record[provisioning][policy])


def set_policy_name(record, policy):
    """
        Returns policy record with new name

        :param record: device provisioning type
        :param policy: policy name
        :return: policy record
    """
    record['policyModel']['reference']['tags']['name'] = policy
    return record


def set_message(record, provisioning, policy, text_msg):
    """
        Returns policy record with a new message

        :param record: policy record
        :param provisioning: device provisioning type
        :param policy: policy name
        :param text_msg: text for a message
        :return: policy record
    """
    return set_in_dict(record, message_path_in_policy_record[provisioning][policy], text_msg)
