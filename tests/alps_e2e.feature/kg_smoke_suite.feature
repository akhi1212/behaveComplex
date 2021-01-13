@E2E_Tests @Regression_Tests @Smoke_Tests @KNOX_GUARD
@env:test5_qa
Feature: E2E smoke suite
  # Automated smoke suite ATP-973

  @ATP-356
    Scenario: Apply Blink Policy from the UI
      Given an enrolled device with "TEST_SHIPPED" policy via web UI
      When the "TEST_BLINK" assigned to the device
      And web UI shows the policy TEST_BLINK is applied on the device
      Then TEST_BLINK message with message text is shown
      And KG app takes the full screen
      And the User is able to dismisses the lock with "OK" button