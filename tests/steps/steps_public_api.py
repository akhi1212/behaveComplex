from datetime import date, datetime
from time import gmtime, sleep

from behave import given, then, when

from config.config import config
from lib import admin_control_lib as acl
from lib import device_control_lib as dcl
from lib import provision_controller_lib as pcl
from lib.policy_control_lib import generate_pin, test_policies
from lib.utils import check_with_delay, get_wait_interval, is_imei_authorized, is_imei_valid, \
    parse_context_table_to_devices_list, parse_context_table_to_dict, time_string_to_policy_format
from lib.utils import get_jwt_token, get_transition_day
from tests.environment import create_device


@given('The "{policy}" has been applied but not yet activated')
@when('the "{policy}" has been applied but not yet activated')
@when('a user changes policy via Admin Public API to "{policy}"')
def step_impl(context, policy):
    dcl.update_device(context.imei, policy)
    context.policy = policy


@given('An admin has default custom properties defined')
@given('a MNO has the following custom properties assigned')
def step_impl(context):
    context.admin_custom_properties = parse_context_table_to_dict(context.table)
    acl.update_admin_record(custom_properties=acl.generate_custom_properties_entity(context.admin_custom_properties))


@given('an enrolled "{provisioning}" device with "{policy}" policy')
@when('an enrolled "{provisioning}" device with "{policy}" policy')
def step_impl(context, provisioning, policy):
    create_device(context, policy=policy, provisioning=provisioning)


@given('The New IMEI is valid and Policy is valid')
@given('The New IMEI is invalid and Policy is valid')
@given('The New IMEI is valid and Policy is invalid')
@given('The New IMEI is invalid and Policy is invalid')
def step_impl(context):
    data = parse_context_table_to_dict(context.table)
    imeis = []
    policies = []
    if isinstance(data['IMEI'], str):   # if context.table contains single line
        # Generate random imei if imei cell is empty
        imeis.append(data['IMEI']) if data['IMEI'] else imeis.append(dcl.generate_random_imei())
        policies.append(data['policy'])
    else:                               # if context.table is multi-line
        imeis += [dcl.generate_random_imei() if not x else x for x in data['IMEI']]
        policies += data['policy']
    zipped = dict(zip(imeis, policies))
    unregistered_devices = [{"imei": i, "assignedPolicy": p} for (i, p) in zipped.items()]
    if not hasattr(context, 'unregistered_devices'):
        context.unregistered_devices = unregistered_devices
    else:
        context.unregistered_devices += unregistered_devices


@given('The Existing IMEI is valid and Policy is valid and New')
@given('The Existing IMEI is valid and Policy is valid and Same')
@given('The Existing IMEI is valid and Policy is invalid')
def step_impl(context):
    create_device(context, policy="TEST_SHIPPED", provisioning='ALPS')
    device = {"imei": context.imei, "assignedPolicy": parse_context_table_to_dict(context.table)["policy"]}
    if not hasattr(context, 'existing_devices'):
        context.existing_devices = [device]
    else:
        context.existing_devices.append(device)


@given('there are holiday configured for "{day}" for the admin account')
def step_impl(context, day):
    today = date.today()
    context.holiday = today.day
    if day == 'tomorrow':
        context.holiday = today.day + 1
    acl.update_admin_record(holidays=[{"dayOfMonth": context.holiday, "month": today.month, "year": today.year}])


@when('The User searches for the imei of the device by calling the /status endpoint on the publicapi')
def step_impl(context):
    get_status = dcl.get_device_status(context.imei)
    context.status_of_the_device = get_status


@given('a user has already registered the below "{provisioning}" IMEI using following contents')
@when('the User registers a "{provisioning}" device via Admin Public API with some custom properties defined and some '
      'empty')
def step_impl(context, provisioning):
    device = parse_context_table_to_devices_list(context.table)[0]
    imei = None if not device['imei'] else device['imei']
    context.expected_custom_properties = {k: v for k, v in device['customProperties'].items() if v}
    create_device(context, policy=device['assignedPolicy'], provisioning=provisioning, imei=imei,
                  custom_properties=device['customProperties'])


@when('The User registers the IMEIs via public API')
def step_impl(context):
    context.response = dcl.register_devices(context.unregistered_devices)
    context.operation = "register"


@when('The User updates the IMEIs via public API')
def step_impl(context):
    devices = context.existing_devices + context.unregistered_devices if hasattr(context, "unregistered_devices") \
        else context.existing_devices
    context.response = dcl.update_devices(devices, ignore_errors=True)
    context.operation = "update"


@when('the user Updates the device details of the following IMEI via public api')
def step_impl(context):
    device = parse_context_table_to_devices_list(context.table)[0]
    context.response = dcl.update_device(context.imei, device['assignedPolicy'],
                                     custom_properties=device['customProperties'])


@when('the user generated the pin via Admin Public API')
def step_impl(context):
    context.response = generate_pin(context.imei, context.provisioning)


@when('it is the transition time in the interval set')
@when('it is the transition time in the new increased interval set')
def step_impl(context):
    transition_days = int(context.auto_transition_settings[context.policy]['hacked_Days'])
    check_with_delay(lambda: datetime.now().minute >= transition_days, times=120, delay=1)


@when('it is the transition time in the interval set for "{policy}" policy')
@then('it is the transition time in the interval set for "{policy}" policy')
def step_impl(context, policy):
    transition_days = transition_days = int(context.auto_transition_settings[policy]['hacked_Days'])
    check_with_delay(lambda: datetime.now().minute >= transition_days, times=120, delay=1)


@when('"{policy}" policy is applied on device')
@when('"currentPolicyId" in the device record is changed to "{policy}" policy')
@given('"{policy}" policy is applied on device')
def step_impl(context, policy):
    activate = False
    imei = context.imei
    provisioning = context.provisioning
    if provisioning == "KNOX_GUARD":
        activate = True
        if pcl.wait_for_kg_status_job(imei, provisioning, "uploadState", expected_value="YES"):
            record = pcl.fetch_provision_records(imei, provisioning)
            assert record['records'][0]['provisioningModel']['deviceReady'] is True, \
                f'KNOX_GUARD device is not ready. Device record should have \'deviceReady\' field as True.'
            uploading_state = pcl.value_from_provisioning(imei, provisioning, "uploadState")
            assert uploading_state == "YES", f'KNOX_GUARD device is not uploaded. Uploading state is {uploading_state}'
        else:
            ValueError("{} device uploading is not finished".format(imei))
    dcl.post_checkin(imei, provisioning, policy, policy, activate)
    device_record = dcl.get_device_record(imei)
    assert device_record['model']['status']['currentPolicyId'] == config.owner + '/' + policy


@then('The correct applied time is seen in assignedPolicyAssignedTime and assignedPolicyActivatedTime is null')
def step_impl(context):
    device_attributes = context.status_of_the_device['devices'][0]
    assert device_attributes['imei'] == context.imei
    assert 'assignedPolicyAssignmentTime' in device_attributes
    assert "assignedPolicyActivatedTime" not in device_attributes


@then('the device will use the default custom property for those not defined')
@then('the device record contains only the custom properties that were defined')
def step_impl(context):
    device_record = dcl.get_device_record(context.imei)
    assert device_record['model']['customProperties'] == context.expected_custom_properties


@then('the response contains "{field1}" and "{field2}"')
@then('The "{pin}" should be successfully generated')
def step_impl(context, **kwargs):
    for field_name in kwargs.values():
        assert field_name in context.response.keys()


@then('"id" in "desiredPolicy" object of the device record {condition} "{policy}"')
@then('"id" in "desiredPolicy" object of the device record {condition} updated policy id "{policy}"')
def step_impl(context, condition, policy):
    predicate = lambda: dcl.get_device_record(context.imei)['model']['desiredPolicy']['id'] == config.owner + '/' + policy
    if condition == 'is changed to':
        assert check_with_delay(predicate, times=120, delay=1), f'desiredPolicy is not {policy}'
    elif condition == 'remains the same':
        for i in range(30):  # will check continuously for 30 sec
            assert predicate(), f'desiredPolicy is not {policy}'
            sleep(1)


@then('"{scheduling_action}" object of the device record correspond to "<test policy>" settings')
def step_impl(context, scheduling_action):
    device_record = dcl.get_device_record(context.imei)
    assert context.policy_record['policyModel']['definition']['definitionV1'][scheduling_action] == \
           device_record['model']['policyDefinition']['definitionV1'][scheduling_action]


@then('SCHEDULED POLICY CHANGE to "{policy}" policy is correctly set according to Transition config')
def step_impl(context, policy):
    device_record = dcl.get_device_record(context.imei)
    assert device_record['model']['calculatedScheduledTransition']['policyId'] == config.owner + '/' + policy
    assert datetime.fromtimestamp(device_record['model']['calculatedScheduledTransition']['triggerTime']).day \
           == get_transition_day(context.active_days, int(context.transition_in_days)), \
           f'triggerTime of scheduled {policy} policy is not correct'


@then('"{param}" is equal to "{day_time}"')
def step_impl(context, param, day_time):
    pcl.wait_for_kg_status_job(context.imei, context.provisioning, param)
    next_action_due_time = pcl.kg_provisioning_action_time(context.imei, context.provisioning)
    if day_time == "start time":
        assert gmtime(time_string_to_policy_format(context.start_time)).tm_hour == next_action_due_time.hour
    elif day_time == "repetition rate":
        if context.delayed_activation_settings.get('repetitionInterval', 'None') == '5m':
            assert (next_action_due_time - datetime.utcnow()).seconds < 5*60, \
                f"nextActionDueTime must be less then 5 minutes according to repetition rate"
    else:
        time_to_wait = get_wait_interval(day_time, context.start_time)
        if len(time_to_wait) > 1:
            assert next_action_due_time.hour == time_to_wait[1]
        assert next_action_due_time.day == (datetime.now().day + time_to_wait[0])


@then('"{param}" is "{value}"')
def step_impl(context, param, value):
    if value != 'None':
        pcl.wait_for_kg_status_job(context.imei, context.provisioning, param, timeout=120)
    val_in_provisioning = str(pcl.value_from_provisioning(context.imei, context.provisioning, param))
    assert val_in_provisioning == value, f'{param} value is: {val_in_provisioning}, must be {value}'


@when('the User "{action}" the device IMEI with the "{policy_state}" policy via public API')
def step_impl(context, action, policy_state):
    assert action in ('register', 'update'), \
        f"Not implemented operation '{action}' for device registration"
    assert policy_state in ('different', "same", "invalid"), \
        f"Not implemented policy state '{policy_state}' for device registration"

    new_policy = {
        "different": lambda: next(policy for policy in test_policies if policy != context.policy),
        "same": lambda: context.policy,
        "invalid": lambda: f"{datetime.now()}"
    }[policy_state]()

    context.result = {
        "register": lambda: dcl.register_device(context.imei, new_policy),
        "update": lambda: dcl.update_device(context.imei, new_policy)
    }[action]()


@then('the API "{result}" to register IMEI with the message')
def step_impl(context, result):
    assert result in ('fails', 'success'), \
        f"Not implemented result '{result}' for device registration"

    operation_result = next(device for device in context.result['devices'])
    assert context.imei in operation_result['imei']
    assert {
        "fails": lambda: 'error' in operation_result,
        "success": lambda: 'error' not in operation_result
    }[result](), f"Unexpected test case result. {operation_result}"


@given('the device is not in the system already')
def step_impl(context):
    context.imei = dcl.generate_random_imei()


@when('a user registers the device IMEI via public API')
def step_impl(context):
    context.registration_data = dcl.register_device(
        context.imei, context.policy if hasattr(context, 'policy') else 'TEST_SHIPPED'
    )


@then('the device record for the IMEI could be retrieved and not empty')
def step_impl(context):
    r_data = dcl.get_device_record(context.imei)
    assert 'imei' in r_data and r_data['imei'] == context.imei, \
        f"Unexpected record received for device with IMEI: {context.imei}"


@given('The IMEI is New = {is_imei_new} and is valid = {imei_is_valid} and Policy policy is valid = {is_policy_valid}')
def step_impl(context, is_imei_new, imei_is_valid, is_policy_valid):

    def str_to_bool(s: str) -> bool:
        return s.lower() in ('true', 'on', 'enable', 'yes')

    context.is_imei_valid = str_to_bool(imei_is_valid)
    context.imei = dcl.generate_random_imei() if context.is_imei_valid else "abcdefghijklmno"
    context.is_policy_valid = str_to_bool(is_policy_valid)
    context.policy = "TEST_SHIPPED" if context.is_policy_valid else f"{datetime.now()}"

    context.is_imei_new = str_to_bool(is_imei_new)
    if not context.is_imei_new:
        dcl.register_device(context.imei, context.policy)


@then('only the Valid New IMEIs with the Valid Policies will be registered')
@then('Errors will be displayed for the failed ones')
def step_impl(context):
    r_data = next(iter(context.registration_data['devices']))
    if context.is_imei_new and context.is_imei_valid and context.is_policy_valid:
        assert 'imei' in r_data
        assert 'error' not in r_data, \
            f"Unexpected result. IS_NEW_IMEI: {context.is_imei_valid}, " \
            f"IS_POLICY_VALID: '{context.is_policy_valid}'. Response data: {r_data}"
    else:
        assert 'error' in r_data, \
            f"Unexpected result. IS_NEW_IMEI: {context.is_imei_new}, " \
            f"IS_POLICY_VALID: '{context.is_policy_valid}'. Response data: {r_data}"


@then('The response should return the correct imei and "{field}" should be None')
@then('The last checkin "{field}" time should be None')
def step_impl(context, **kwargs):
    device_status = context.status_of_the_device['devices'][0]
    assert device_status['imei'] == context.imei
    for field in kwargs.values():
        assert device_status.get(field) is None


@then('Applied and activated time values are seen under "{field1}" and "{field2}" fields')
@then('The "{field1}" flag is seen')
def step_impl(context, **kwargs):
    device_status = context.status_of_the_device['devices'][0]
    for field in kwargs.values():
        assert field in device_status.keys(), f'{field} is not present in device status response data'
        if field.endswith('Time'):
            try:
                datetime.strptime(device_status.get(field), '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                raise AssertionError(f"Incorrect data format of {field}: {device_status.get(field)}, "
                                     f"should be yyyy-mm-ddTh:m:sZ")


@given('a user generates JWT with "{permissions}" permission parameter')
def step_impl(context, permissions):
    context.permissions = permissions.split()
    context.jwt_token = get_jwt_token(permission_scope=context.permissions)


@when('a user makes a "{function}" call using generated JWT token')
def step_impl(context, function):
    if function == "get_device_status":
        context.response = dcl.get_device_status(context.imei, jwt_token=context.jwt_token, ignore_errors=True)
    elif function == "register_device":
        context.imei = dcl.generate_random_imei(provisioning=context.provisioning)
        context.response = dcl.register_device(context.imei, context.policy, jwt_token=context.jwt_token,
                                           ignore_errors=True)
    elif function == "generate_pin":
        context.response = generate_pin(context.imei, context.provisioning, jwt_token=context.jwt_token,
                                        ignore_errors=True)
    elif function == "update_device":
        context.response = dcl.update_device(context.imei, context.policy,
                                         custom_properties=context.admin_custom_properties,
                                         jwt_token=context.jwt_token, ignore_errors=True)
    else:
        assert False, f"Unexpected function '{function}' has been invoked"


@then('a user is able "{expected_result}" to make a "{function}" function call')
def step_impl(context, expected_result, function):
    actual_result = "False" if 'error' in context.response else "True"
    assert actual_result == expected_result, \
        f'Function: {function}, permissions: {context.permissions}. ' \
        f'Actual Result: {actual_result}, Expected Result: {expected_result}'


@then('Only the Valid existing IMEIs with the Valid Policies will be updated')
def step_impl(context):
    successfully_updated_imeis = [d['imei'] for d in context.response['devices'] if 'error' not in d.keys()]
    assert successfully_updated_imeis.sort() == [d['imei'] for d in context.existing_devices if
                                                 d['assignedPolicy'] in test_policies.keys()].sort(), \
        "Device(s) with invalid policy was successfully updated or it didn't exist before update"


@then('Errors will be displayed "{message}" for the failed ones')
def step_impl(context, message):
    failures = [d for d in context.response['devices'] if 'error' in d.keys()]
    for fail in failures:
        imei = fail['imei']
        err_code = fail['error']['code']
        err_msg = fail['error']['error']
        # Common checks for 'register_devices' and 'update_devices'
        # Invalid or unauthorized IMEI error overrides other errors
        if not is_imei_valid(imei):
            assert err_code == "IMEI_INVALID"
            assert err_msg == f"Invalid IMEI {imei} provided."
            continue
        elif not is_imei_authorized(imei):
            assert err_code == "TAC_NOT_AUTHORISED"
            assert err_msg == f"Owner is not authorised to use this TAC."
            continue
        # Checks for 'update_devices'
        if context.operation == 'update':
            # If device was not registered before update
            if [d for d in context.unregistered_devices if imei == d['imei']]:
                assert err_code == "IMEI_INVALID"
                assert err_msg == f"Could not find device."
                continue
            # If device was registered before update
            elif [d for d in context.existing_devices if imei == d['imei']]:
                # If policy is invalid
                if [d for d in context.existing_devices if imei == d['imei']
                        and d['assignedPolicy'] not in test_policies.keys()]:
                    assert err_code == "DATA_ERROR"
                    assert err_msg.startswith("Request for policy reference") and \
                           err_msg.endswith("did not return one record with valid policy model and policy reference.")
                    continue
                else:
                    raise AssertionError(f"Unexpected error was returned upon "
                                         f"updating already registered device: {err_code}, {err_msg}")


@then('the device is successfully updated')
def step_impl(context):
    assert not [d for d in context.response['devices'] if 'error' in d.keys()]


@then('the custom property values for below is updated to "NULL"')
def step_impl(context):
    null_props = context.table.headings
    device_records = [dcl.get_device_record(d['imei']) for d in context.response['devices']]
    for record in device_records:
        for prop in null_props:
            assert prop not in record['model']['customProperties'].keys(), f"Property '{prop}' is not None"


@then('the "{property_name}" property value for the registered devices should be "{value}"')
def step_impl(context, property_name, value):
    device_records = [dcl.get_device_record(d['imei']) for d in context.response['devices']]
    for record in device_records:
        assert record['model']['customProperties'][property_name] == value


@then('the "{property_name}" property value for the MNO should be "{value}"')
def step_impl(context, property_name, value):
    admin_record = acl.get_admin_record(config.id_test_admin)
    assert admin_record['model']['customProperties'][property_name]['defaultValue'] == value


@then('the property values for the below should not be changed')
def step_impl(context):
    data = parse_context_table_to_dict(context.table)
    expected_props = dict(zip(data['custom properties'], data['custom values']))
    for d in context.response['devices']:
        actual_props = dcl.get_device_record(d['imei'])['model']['customProperties']
        assert set(expected_props.items()).issubset(actual_props.items())
