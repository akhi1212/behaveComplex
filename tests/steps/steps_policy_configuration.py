import copy

from behave import given, when
from datetime import datetime
from lib import policy_control_lib as pcl
from lib.utils import parse_context_table_to_dict, time_string_to_policy_format, repetition_value_to_seconds


@given('a "{policy}" policy with the Automated Transition settings')
@when('a "{policy}" policy with the Automated Transition settings')
def step_impl(context, policy):
    if not hasattr(context, 'auto_transition_settings'):
        context.auto_transition_settings = {}
    context.auto_transition_settings[policy] = parse_context_table_to_dict(context.table)
    context.active_days = context.auto_transition_settings[policy]['Days active']
    context.transition_in_days = context.auto_transition_settings[policy]['Days']
    context.policy_record = pcl.configure_automated_transition(policy,
                                                           from_state=context.auto_transition_settings[policy]['From'],
                                                           days=context.transition_in_days,
                                                           reference_policy=context.auto_transition_settings[policy]['ID'],
                                                           days_active=context.active_days,
                                                           exclude_holidays=context.auto_transition_settings[policy][
                                                               'Exclude Holidays'],
                                                           days_to_minutes=context.days_to_minutes)
    pcl.update_policy_record(policy, policy_record=context.policy_record)
    context.auto_transition_settings[policy]['hacked_Days'] = \
        context.policy_record['policyModel']['definition']['definitionV1']['serverScheduledTransition']['days']


@given('a "{policy}" configured with delayed activation')
def step_impl(context, policy):
    context.delayed_activation_settings = parse_context_table_to_dict(context.table)
    exclude_holidays = context.delayed_activation_settings.get('excludeHolidays', False)
    assigned_before_window = context.delayed_activation_settings.get('assignedTimeBeforeActivationWindow', None)
    if exclude_holidays == "True":
        exclude_holidays = True
    elif exclude_holidays == "False":
        exclude_holidays = False
    if assigned_before_window == "True":
        context.start_time = str(datetime.now().hour + 2)
        if context.delayed_activation_settings.get("holiday", "") == "tomorrow":
            context.start_time = str((int(context.start_time) + (25 - int(context.start_time))) % 24)
        context.end_time = str(datetime.now().hour + 3)
    else:
        context.start_time = str(datetime.now().hour - 3)
        context.end_time = str(datetime.now().hour + 3)
    repetition_interval = context.delayed_activation_settings.get('repetitionInterval', None)
    context.repetition_interval = repetition_interval if repetition_interval is None or repetition_interval == 'None' \
        else repetition_value_to_seconds(repetition_interval)
    context.policy_record = pcl.configure_delayed_activation(policy,
                                                         start_time=time_string_to_policy_format(context.start_time),
                                                         end_time=time_string_to_policy_format(context.end_time),
                                                         days=context.delayed_activation_settings['Days active'],
                                                         exclude_holidays=exclude_holidays,
                                                         once_per_day=context.delayed_activation_settings.get(
                                                             'oncePerDay', False),
                                                         repetition_interval=context.repetition_interval,
                                                         non_dismissible=context.delayed_activation_settings.get(
                                                             'nonDismissible', False),
                                                         activation_duration=context.delayed_activation_settings.get(
                                                             'activationDuration', None))
    pcl.update_policy_record(policy, policy_record=context.policy_record)


@when('changes "{policy}" policy with next settings: days increased by {add_days}, id - "{reference_policy}"')
def step_impl(context, policy, add_days, reference_policy):
    days = int(context.auto_transition_settings[policy]['Days']) + int(add_days)
    context.policy_record = pcl.configure_automated_transition(policy, days=days, reference_policy=reference_policy)
    pcl.update_policy_record(policy, policy_record=context.policy_record)


@when('the automated transition disabled for the "{policy}" policy')
def step_impl(context, policy):
    context.policy_record = pcl.remove_transition_settings(policy)
    pcl.update_policy_record(policy, policy_record=context.policy_record)


@given('a "{policy}" configured with next parameters')
def step_impl(context, policy):
    context.localized_settings = parse_context_table_to_dict(context.table)
    context.policy = policy
    context.policy_record = pcl.update_lock_policy_w_localized_text(policy, context.localized_settings['localisedTitle'],
                                                                context.localized_settings['localisedMessage'],
                                                                context.localized_settings['addLocaleOverridesTitle'])
    pcl.update_policy_record(policy, policy_record=context.policy_record)


@given('a new {policy_type} policy "{policy_name}" configured with next message')
def step_impl(context, policy_type, policy_name):
    assert policy_type in pcl.policy_name_from_type.keys(), \
        f"Not implemented for '{policy_type}' policy type"
    text_msg = parse_context_table_to_dict(context.table)['Text_message']
    context.policy_record = copy.deepcopy(pcl.test_policies[pcl.policy_name_from_type[policy_type]])
    context.policy_record = pcl.set_policy_name(context.policy_record, policy_name)
    context.policy_record = pcl.set_message(context.policy_record, context.provisioning, policy_name, text_msg)
    pcl.update_policy_record(policy_name, policy_record=context.policy_record)
