from behave import then
from lib import policy_control_lib as pcl


@then('{policy_id} message with message text is shown')
def step_impl(context, policy_id):
    message = context.device.security_app.home_screen.get_message()
    assert pcl.get_actual_message(policy_id, context.provisioning) == message["text"]


@then("KG app takes the full screen")
def step_impl(context):
    assert context.device.security_app.get_size() == context.device.get_screen_size()


@then('the User is able to dismisses the lock with "OK" button')
def step_impl(context):
    context.device.security_app.home_screen.click_ok_btn()
    assert not context.device.security_app.home_screen.is_open()
