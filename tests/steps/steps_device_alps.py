from typing import Optional

import polling as polling
from behave import given, when, then, use_fixture, register_type

from tests.environment import fixture_with_traceback
from lib import policy_control_lib as pcl


register_type(eval=lambda string_: eval(string_))


@fixture_with_traceback
def with_language_set_to(context, language):
    initial_language, _ = context.device.get_locale()
    context.device.settings.open("Language and region")
    context.device.settings.set_region("United Kingdom")
    try:
        context.device.settings.set_language(language)
        device_lang, _ = context.device.get_locale()
        context.device.press_button("home")
        assert device_lang == language
        yield
    finally:
        context.device.settings.open("Language and region")
        context.device.settings.set_language(initial_language)
        context.device.press_button("home")


@given('the device configured with {language} language')
def step_impl(context, language):
    use_fixture(with_language_set_to, context, language)


@given("proceed with enrollment")
def step_impl(context):
    if context.device.info.manufacturer not in {"Samsung", "Google"}:
        context.device.settings.open_app_info("ALPS").tap_gear()
        context.device.security_app.maintenance_menu.tap_check_in()
        context.device.press_button("home")


@when('the device is locked by policy with id {policy_id} within {timeout:eval} seconds')
def step_impl(context, policy_id: str, timeout: Optional[int] = None):  # noqa
    """
    :param policy_id: policy without owner
    :param timeout: if the timeout is None, the check-in interval from the policy will be used
    """
    if timeout is None:
        policy_definition = pcl.get_policy_record(policy_id=policy_id, from_server=True)["policyModel"]["definition"]
        try:
            timeout = policy_definition["checkin"]["period"]
        except KeyError:
            policy_definition = policy_definition["definitionV2"] or policy_definition["definitionV1"]
            timeout = policy_definition["checkin"]["period"]
    timeout += 10
    polling.poll(
        target=context.device.is_screen_locked,
        step=2,
        timeout=timeout,
    )


@then('ALPS message with {localised_title} and {localised_msg} is shown')
def step_impl(context, localised_title, localised_msg):
    message = context.device.security_app.home_screen.get_message()
    assert localised_title.strip('"') == message["title"]
    assert localised_msg.strip('"') == message["text"]


@then("ALPS app takes the full screen")
def step_impl(context):
    assert context.device.security_app.get_size() == context.device.get_screen_size()
