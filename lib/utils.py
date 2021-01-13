import copy
import logging
import csv
import importlib
import os
import re
import time
from csv import DictReader
from datetime import datetime as dt
from datetime import timedelta
from subprocess import Popen, PIPE
from typing import Set, List, Dict, Any

import requests
from behave.model import Table

import env
from config.config import config
from config.config import get_csv_download_dir
from lib.admin_control_lib import get_admin_holidays


logger = logging.getLogger(config.LOGGER_NAME + f".{__name__}")


def default_cmd_error_handler(cmd, process, stdout=None, stderr=None):
    raise RuntimeError("%r failed, status code %s stdout %r stderr %r" % (
        cmd, process.returncode, stdout, stderr))


def run_in_command_line(cmd, error_handler=default_cmd_error_handler, need_output=True):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    if need_output:
        stdout, stderr = process.communicate()
        process.wait()
        if process.returncode != 0:
            error_handler(cmd, process, stdout, stderr)
        return stdout, stderr
    else:
        time.sleep(2)
        return process


def open_file_from_resources(path_to_file):
    return open(os.path.dirname(__file__) + r'/../resources/' + path_to_file, 'rb')


def get_jwt_token(permission_scope: list = None):
    jar_file_path = os.path.dirname(__file__) + r'/../resources/alps-admin-api-2.2.4-boot.jar'
    creds_file_path = os.path.dirname(__file__) + r'/../resources/credentials.json'

    custom_scope = _generate_custom_scope(permission_scope) if permission_scope else list()
    token_gen_cmd = [
        "java", "-cp", jar_file_path,
        "-Dloader.main=com.trustonic.alps.adminapi.utils.JwtTokenGenerator",
        "org.springframework.boot.loader.PropertiesLauncher",
        "-cf", creds_file_path,
        "-k", "test-admin"] + custom_scope

    stdout, stderr = run_in_command_line(token_gen_cmd)
    jwt_token = "Bearer " + stdout.split()[-1].decode("utf-8")
    return jwt_token


def _generate_custom_scope(scope: list):
    allowed_scope = ["register", "status", "update", "getpin"]
    custom_scope = list()
    [custom_scope.extend(['-s', f'devices:{s}']) for s in scope if s in allowed_scope]
    if not custom_scope:
        raise ValueError(f"Custom scope for jwt token generation is not defined.\n"
                         f"Input scope: {scope}")

    return custom_scope


def get_admin_access_token():
    data = {"username": config.KC_USER_ADMIN, "password": config.KC_PASSWORD, "grant_type": "password",
            "client_id": config.KC_CLIENT_ID, "client_secret": config.KC_CLIENT_SECRET}

    response = requests.post(config.hosts.KC_TOKEN_URL, data=data)
    token = response.json()["access_token"]

    return "Bearer " + token


def check_with_delay(predicate, expected_state=True, times=20, delay=0.5):
    result = None
    for i in range(0, times):
        result = predicate()
        if result == expected_state:
            return expected_state
        time.sleep(delay)
    return result


def parse_context_table_to_dict(table):
    res = {}
    for row in table:
        for name in row.headings:
            if len(table.rows) > 1:
                if name in res:
                    res[name].append(row[name])
                else:
                    res[name] = [row[name]]
            else:
                res[name] = row[name]
    return res


def parse_context_table_to_devices_list(table: Table) -> List[Dict[str, Any]]:
    """
    Parse behave table with data like imei, policy and move the rest to customProperties
    :param table: behave table
    :return: list of devices (dictionary with keys: imei, assignedPolicy, customProperties)
    """
    devices = []
    tb = copy.deepcopy(table)
    for row in tb:
        device = {'imei': row.get("imei"), 'assignedPolicy': row.get("policy"),
                  'customProperties': {k: v for k, v in row.as_dict().items() if k not in ["imei", "policy"]}}
        devices.append(device)
    return devices


def make_enrol_device_file(csv_file_content):
    headers = list(csv_file_content.keys())
    data_lines = []
    multiple_imei = False
    if type(csv_file_content['imei']) == list:
        multiple_imei = True
        for i in range(len(csv_file_content['imei'])):
            data_line = []
            for field in csv_file_content.keys():
                data_line.append(csv_file_content[field][i])
            data_lines.append(data_line)
    else:
        for field in csv_file_content.keys():
            data_lines.append(csv_file_content[field])

    file_path = os.path.dirname(__file__) + r'/../resources/test_device_enrol.csv'

    with open(file_path, "w") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headers)
        if multiple_imei:
            for data_line in data_lines:
                writer.writerow(data_line)
        else:
            writer.writerow(data_lines)

    return file_path


def time_string_to_policy_format(time_string: str):
    """
        Converts time string to seconds
    :param time_string: time string to convert, must have 00:00 format
    """
    if time_string.find("+") != -1 and time_string.find("now") != -1:
        time_string = str(dt.now().hour + int(time_string.split("+")[1]))
    if time_string.find(":") == -1:
        time_string += ":00"
    if 0 > int(time_string.split(":")[0]) > 24 or 0 > int(time_string.split(":")[1]) > 59:
        raise ValueError("Invalid time value. Can't convert {} time to 24 hours format".format(time_string))
    return sum(x * int(t) for x, t in zip([3600, 60], time_string.split(":")))


def repetition_value_to_seconds(time_string: str):
    """
        Converts repetition time value to  policy format
    :param time_string: time string to convert.
    Could be 1d - day, 2h - hour or 3m - minute
    """
    if time_string.find("d") != -1:
        return time_string_to_policy_format(time_string[:-1]) * 24
    elif time_string.find("h") != -1:
        return time_string_to_policy_format(time_string[:-1])
    elif time_string.find("m") != -1:
        return time_string_to_policy_format("00:{}".format(time_string[:-1]))


def get_wait_interval(value_to_wait: str, start_time: str):
    """
        Return tuple with wait interval in case of excluding existing holidays for delayed activation
    :param value_to_wait: string with time value to wait.
    :param start_time: string with activation window. start time.
    """
    days_to_wait = 0
    hours_to_wait = 0

    if value_to_wait == 'day after tomorrow':
        return 2
    elif value_to_wait == 'in one week':
        return 7
    elif value_to_wait.find("+") != -1:
        day = value_to_wait.split(" + ")[0]
        hours_to_wait = value_to_wait.split(" + ")[1:]
        if len(hours_to_wait) == 1:
            hours_to_wait = hours_to_wait[0]
            if hours_to_wait == "start time":
                hours_to_wait = int(start_time)
        if day == 'day after tomorrow':
            days_to_wait += 2
        if hours_to_wait > 24:
            days_to_wait += hours_to_wait / 24
            hours_to_wait %= 24

    return days_to_wait, hours_to_wait


def validate_unix_time(timestamp: str, expected_csv_value):
    """"
        Verifies if timestamp is valid unix timestamp
        :param timestamp - timestamp to be verified
    """
    try:
        converted_timestamp = dt.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        if int((dt.strptime(converted_timestamp, "%Y-%m-%d %H:%M:%S")).year) != dt.now().year or \
            int((dt.strptime(converted_timestamp, "%Y-%m-%d %H:%M:%S")).day) > 31 or \
            int((dt.strptime(converted_timestamp, "%Y-%m-%d %H:%M:%S")).hour) > 24 or \
            int((dt.strptime(converted_timestamp, "%Y-%m-%d %H:%M:%S")).minute) > 59:
            return False
        else:
            if expected_csv_value == "UNIX time":
                return True
    except Exception as e:
        raise BaseException("Fail to convert {0} to datetime format. {1}".format(timestamp, e))


def check_csv_report(expected_csv_content: dict, csv_file_path: str):
    """"
        Check if field from expected_csv_content is in csv report with needed value
        :param expected_csv_content - dictionary with expected field names and it's values
        :param csv_file_path - path do downloaded CSV report
    """
    with open(csv_file_path, 'r') as exported_scv:
        csv_reader = DictReader(exported_scv)
        for field_name, expected_value in expected_csv_content.items():
            for row in csv_reader:
                csv_value = row.get(field_name, None)
                if csv_value is not None:
                    assert validate_unix_time(csv_value, expected_value) is True, f"{field_name} values is CSV is {csv_value}, must be: {expected_value}"
                else:
                    raise ValueError("There is no {} field in downloaded report".format(field_name))


def empty_download_folder():
    """"
        Delets all files in tests download folder
    """
    download_dir = get_csv_download_dir()
    dowloaded_files = os.listdir(download_dir)
    if len(dowloaded_files) >= 1:
        for file in dowloaded_files:
            os.remove(os.path.join(download_dir, file))


def get_transition_day(active_days: str, transition_in_days: int):
    """"
        Returns scheduled transition day, day of month format
        :param active_days - days during policy is active
        :param transition_in_days - scheduled transition days count
    """
    days_to_wait = 0
    tomorrow = dt.today().day + 1
    holidays_list = get_admin_holidays()
    if active_days == "today":
        if transition_in_days == 1:
            if dt.today().day + 7 in holidays_list:
                days_to_wait = 14
            else:
                days_to_wait = 7
        else:
            if dt.today().day + transition_in_days in holidays_list:
                days_to_wait = transition_in_days + 1
            else:
                days_to_wait = transition_in_days
    elif active_days == "except tomorrow":
        if dt.today().day + 2 in holidays_list:
            days_to_wait = 3
        else:
            days_to_wait = 2
    else:
        if tomorrow in holidays_list:
            days_to_wait = 2
        else:
            days_to_wait = 1
    transition_day = (dt.now() + timedelta(days=days_to_wait)).day
    logger.info(f"utils:get_transition_day:transition day is set to {transition_day} day of month")
    return transition_day


def is_imei_valid(imei: str):
    """
    Check if provided imei is valid

    :param imei: imei
    :return: True, if imei is valid
    """
    return re.compile("\d{15}").fullmatch(imei)


def is_imei_authorized(imei: str):
    """
    Check if provided imei is authorized

    :param imei: imei
    :return: True, if imei is authorized
    """
    return imei.startswith(config.test_tacs["ALPS"]) or imei.startswith(config.test_tacs["KNOX_GUARD"])


def get_classes_from_dir(class_type: type, path: str) -> Set[type]:
    root_dir = env.PROJ_ROOT
    classes: Set[type] = set()

    for dir_path, dir_names, file_names in os.walk(path):
        for fn in file_names:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dir_path, fn)
            import_str = ".".join(fp.replace(root_dir, "")[:-3].lstrip(os.sep).split(os.sep))
            module = importlib.import_module(import_str)
            for obj in module.__dict__.values():
                if isinstance(obj, type) and issubclass(obj, class_type):
                    classes.add(obj)
        break
    return classes


def get_timestamp() -> str:
    return dt.now().strftime('%Y_%b_%d_%H-%M-%S.%f')
