@KNOX_GUARD @ALPS_Client
@API_Tests @Regression_Tests @Smoke_Tests
Feature: Public API tests


  @ATP-271
  Scenario: Register valid IMEI via Public API
    Given the device is not in the system already
    When a user registers the device IMEI via public API
    Then the device record for the IMEI could be retrieved and not empty


  @ATP-292
  Scenario Outline: Register existing IMEI with different policy via Public API
    Given an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When The User "<action>" the device IMEI with the "<policy_state>" policy via public API
    Then The API "<result>" to register IMEI with the message

    Examples:
      |policy_state |action  |result |
      |different    |register|fails  |
      |same         |register|fails  |
      |invalid      |register|fails  |
      |different    |update  |success|
      |same         |update  |success|


  @ATP-319
  Scenario Outline: Register multiple valid and invalid IMEIs with valid and invalid policies via Public API
    Given The IMEI is New = <is_imei_new> and is valid = <is_imei_valid> and Policy policy is valid = <is_policy_valid>
    When a user registers the device IMEI via public API
    Then only the Valid New IMEIs with the Valid Policies will be registered
    And Errors will be displayed for the failed ones

    Examples:
      |is_imei_new|is_imei_valid|is_policy_valid|
      |true       |true         |true           |
      |true       |true         |false          |
      |true       |false        |true           |
      |true       |false        |false          |
      |false      |true         |true           |
      |false      |true         |false          |


  @ALPS-513 @ALPS-514
  Scenario Outline: Public API: Check Policy Application when Activation Time is null
    Given The "<policy>" has been applied but not yet activated
    When The User searches for the imei of the device by calling the /status endpoint on the publicapi
    Then The correct applied time is seen in assignedPolicyAssignedTime and assignedPolicyActivatedTime is null

    Examples:
      | policy       | imei            | provisioning |
      | TEST_SHIPPED | 345678901234569 | KNOX_GUARD   |
      | TEST_SHIPPED | 862243047883569 | ALPS         |


  @ATP-898
  Scenario: ALPS Client | Admin Public API | ALPS test custom messages on registration
    Given An admin has default custom properties defined
      | CustomMessage   | MontoDeDeuda |
      | CustomMessage   | MontoDeDeuda |
    When the User registers a "ALPS" device via Admin Public API with some custom properties defined and some empty
      | imei            | policy       | CustomMessage   | MontoDeDeuda |
      | <random_imei>   | TEST_SHIPPED | NEW VALUE       |              |
    Then the device will use the default custom property for those not defined
    And the device record contains only the custom properties that were defined


  @ATP-899
  Scenario: ALPS Client | Admin Public API | Check pin unlock
    Given an enrolled "ALPS" device with "TEST_LOCK" policy
    When the user generated the pin via Admin Public API
    Then the response contains "imei" and "pin"


  @ATP-900
  Scenario: ALPS Client | Admin Public API | Unlock phone via policy
    Given an enrolled "ALPS" device with "TEST_LOCK" policy
    When a user changes policy via Admin Public API to "TEST_UNLOCK"
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_UNLOCK"


  @ATP-901 @ATP-902 @ATP-905
  Scenario Outline: ALPS Client | Admin Public API | Scheduled actions | Applying the Delayed <policy> policy
    Given a "<policy>" configured with delayed activation
      | assignedTimeBeforeActivationWindow| delayInitialActivation | Days active | excludeHolidays   |
      | True                              | True                   | All         | <excludeHolidays> |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "<policy>"
    Then "id" in "desiredPolicy" object of the device record is changed to "<policy>"
    And "alpsActionScheduling" object of the device record correspond to "<test policy>" settings

    Examples:
      | policy            | excludeHolidays |
      | TEST_LOCK         | False           |
      | TEST_MESSAGE      | False           |
      | TEST_NOTIFICATION | True            |


  @ATP-903 @ATP-912 @slow
  @env:local
  Scenario Outline: <Provisioning> Client| Admin Public API | Automated Transition | From a <policy> policy Assigned to a <ID> policy
         all days active
    Given a "<policy>" policy with the Automated Transition settings
      | Days | From     | ID   | Days active | Exclude Holidays |
      | 1    | ASSIGNED | <ID> | All         | unchecked      |
    And an enrolled "<Provisioning>" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "<policy>"
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "<ID>"

    Examples:
      | policy            | ID                | Provisioning |
      | TEST_NOTIFICATION | TEST_MESSAGE      | ALPS         |
      | TEST_MESSAGE      | TEST_LOCK         | ALPS         |
      | TEST_MESSAGE      | TEST_NOTIFICATION | ALPS         |
      | TEST_NOTIFICATION | TEST_LOCK         | ALPS         |
      | TEST_LOCK         | TEST_MESSAGE      | ALPS         |
      | TEST_LOCK         | TEST_NOTIFICATION | ALPS         |


  @ATP-904 @ATP-911 @slow
  @env:local
  Scenario Outline: <Provisioning> Client | Admin Public API | Automated Transition | From a <policy> Activated to a <ID> policy,
            all days active
    Given a "<policy>" policy with the Automated Transition settings
      | Days | From     | ID   | Days active | Exclude Holidays |
      | 1    | ACTIVATED| <ID> | All         | Unchecked        |
    And an enrolled "<Provisioning>" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "<policy>"
    And "<policy>" policy is applied on device
    And "currentPolicyId" in the device record is changed to "<policy>" policy
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "<ID>"

    Examples:
      | policy       | ID           | Provisioning |
      | TEST_LOCK    | TEST_MESSAGE | ALPS         |
      | TEST_MESSAGE | TEST_RELEASE | ALPS         |


  @ATP-906
  @env:test4_qa
  Scenario: ALPS Client | Admin Public API | Automated Transition | From a policy Activated to a /MESSAGE policy,
            excluding holidays
    Given there are holiday configured for "tomorrow" for the admin account
    And a "TEST_LOCK" policy with the Automated Transition settings
      | Days | From      | ID               | Days active | Exclude Holidays |
      | 1    | ACTIVATED | TEST_MESSAGE     | All         | Checked          |
    And an enrolled "ALPS" device with "TEST_LOCK" policy
    When "TEST_LOCK" policy is applied on device
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_LOCK"
    And SCHEDULED POLICY CHANGE to "TEST_MESSAGE" policy is correctly set according to Transition config


  @ATP-907
  @env:test4_qa
  Scenario: ALPS Client | Admin Public API | Automated Transition | From a policy Assigned to a /MESSAGE policy,
            during inactive days
    Given a "TEST_LOCK" policy with the Automated Transition settings
      | Days | From     | ID               | Days active            | Exclude Holidays |
      | 1    | ASSIGNED | TEST_MESSAGE     | except tomorrow        | Unchecked        |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "TEST_LOCK"
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_LOCK"
    And SCHEDULED POLICY CHANGE to "TEST_MESSAGE" policy is correctly set according to Transition config


  @ATP-908 @slow @skip  # skipped due to ALPS-3555
  @env:local
  Scenario: ALPS Client | Admin Public API | Automated Transition | Transition settings added after the policy has been
            activated on the device
    Given an enrolled "ALPS" device with "TEST_MESSAGE" policy
    And "TEST_MESSAGE" policy is applied on device
    When a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From     | ID            | Days active | Exclude Holidays |
      | 1    | ACTIVATED| TEST_LOCK     | All         | Unchecked        |
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_LOCK"


  @ATP-909 @slow
  @env:local
  Scenario: ALPS Client | Admin Public API | Automated Transition | Transition settings removed after the policy
            has been activated on the device
    Given a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From      | ID            | Days active | Exclude Holidays |
      | 1    | ACTIVATED | TEST_LOCK     | All         | Unchecked        |
    And an enrolled "ALPS" device with "TEST_MESSAGE" policy
    And "TEST_MESSAGE" policy is applied on device
    When the automated transition disabled for the "TEST_MESSAGE" policy
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record remains the same "TEST_MESSAGE"


  @ATP-910 @slow  @skip  # skipped due to ALPS-3555
  @env:local
  Scenario: ALPS Client | Admin Public API | Automated Transition | Transition settings changed after the policy
            has been activated on the device
    Given a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From      | ID            | Days active | Exclude Holidays |
      | 1    | ASSIGNED  | TEST_LOCK     | All         | Unchecked        |
    And an enrolled "ALPS" device with "TEST_MESSAGE" policy
    And "TEST_MESSAGE" policy is applied on device
    When a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From      | ID                | Days active | Exclude Holidays |
      | 2    | ACTIVATED | TEST_NOTIFICATION | All         | unchecked        |
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_NOTIFICATION"


  @ATP-914 @slow
  @env:local
  Scenario: ALPS Client | Admin Public API | Policy transition from ASSIGNED in 1 day if the original policy is already ACTIVATED
    Given a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From     | ID          | Days active | Exclude Holidays |
      | 1    | ASSIGNED | TEST_LOCK   | All         | Unchecked        |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "TEST_MESSAGE"
    And "TEST_MESSAGE" policy is applied on device
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_LOCK"


  @ATP-915 @slow
  @env:local
  Scenario: ALPS Client | Admin Public API | Policy transition from ACTIVATED in 1 day if the original policy is still ASSIGNED
    Given a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From      | ID          | Days active | Exclude Holidays |
      | 1    | ACTIVATED | TEST_LOCK   | All         | Unchecked        |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When the "TEST_MESSAGE" has been applied but not yet activated
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record remains the same "TEST_MESSAGE"


  @ATP-916 @env:test4_qa
    Scenario: ALPS Client | Admin Public API | Automated Transition | Policy transition in 1 day in case
            if next day is inactive
    Given a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From     | ID               | Days active | Exclude Holidays |
      | 1    | ASSIGNED | TEST_LOCK        | today       | Unchecked        |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "TEST_MESSAGE"
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_MESSAGE"
    And SCHEDULED POLICY CHANGE to "TEST_LOCK" policy is correctly set according to Transition config


  @ATP-918 @slow
  @env:local
  Scenario: ALPS Client | Admin Public API | Policy transition after changing policy settings
    Given a "TEST_LOCK" policy with the Automated Transition settings
      | Days | From     | ID            | Days active | Exclude Holidays |
      | 1    | ASSIGNED | TEST_MESSAGE  | All         | Unchecked        |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "TEST_LOCK"
    And changes "TEST_LOCK" policy with next settings: days increased by 1, id - "TEST_NOTIFICATION"
    And it is the transition time in the new increased interval set
    Then "id" in "desiredPolicy" object of the device record is changed to updated policy id "TEST_NOTIFICATION"


  @ATP-919 @slow
  @env:local
  Scenario Outline: ALPS Client | Admin Public API | Automated Transition | "<policy>" transition after disabling automated transition
    Given a "<policy>" policy with the Automated Transition settings
      | Days  | From     | ID      | Days active | Exclude Holidays |
      | 1     | ASSIGNED | "<id>"  | All         | Unchecked        |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "<policy>"
    And the automated transition disabled for the "<policy>" policy
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record remains the same "<policy>"

  Examples:
    | policy       | id	                |
    | TEST_LOCK    | TEST_MESSAGE       |
    | TEST_MESSAGE | TEST_LOCK          |
    | TEST_LOCK    | TEST_NOTIFICATION  |


  @ATP-920 @ATP-1033 @slow
  @env:local
  Scenario Outline: <provisioning> Client | Admin Public API | Automated Transition | Transition loop
    Given a "TEST_MESSAGE" policy with the Automated Transition settings
      | Days | From     | ID            | Days active | Exclude Holidays |
      | 1    | ASSIGNED | TEST_LOCK     | All         | Unchecked        |
    And a "TEST_LOCK" policy with the Automated Transition settings
      | Days | From     | ID               | Days active | Exclude Holidays |
      | 3    | ASSIGNED | TEST_MESSAGE     | All         | Unchecked        |
    And an enrolled "<provisioning>" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "TEST_MESSAGE"
    And it is the transition time in the interval set for "TEST_MESSAGE" policy
    Then "id" in "desiredPolicy" object of the device record is changed to "TEST_LOCK"
    And it is the transition time in the interval set for "TEST_LOCK" policy
    And "id" in "desiredPolicy" object of the device record is changed to "TEST_MESSAGE"
  Examples:
    | provisioning |
    | ALPS         |
    | KNOX_GUARD   |


  @ATP-684
  Scenario: KG | Scheduled actions | Applying the Delayed Message policy
    Given a "TEST_MESSAGE" configured with delayed activation
      | assignedTimeBeforeActivationWindow | delayInitialActivation | Days active | excludeHolidays |
      | True                               | True                   | All         | False           |
    When an enrolled "KNOX_GUARD" device with "TEST_MESSAGE" policy
    And "TEST_MESSAGE" policy is applied on device
    Then "kgActionScheduling" object of the device record correspond to "<test policy>" settings
    And "nextActionDueTime" is equal to "start time"


  @ATP-700
  Scenario: KG | Scheduled actions | Applying the Delayed Lock policy
    Given a "TEST_LOCK" configured with delayed activation
      | assignedTimeBeforeActivationWindow | delayInitialActivation | Days active | excludeHolidays |
      | False                              | True                   | All         | False           |
    And an enrolled "KNOX_GUARD" device with "TEST_LOCK" policy
    When "TEST_LOCK" policy is applied on device
    Then "kgActionScheduling" object of the device record correspond to "<test policy>" settings
    And "lastCommandTargetType" is "LOCK"
    And "nextActionDueTime" is "None"

  @ATP-917
  @env:test4_qa
  Scenario Outline: ALPS Client | Admin Public API | Policy transition in 1 day in case if the next day is a holiday
    Given there are holiday configured for "<holiday>" for the admin account
    And a "<policy>" policy with the Automated Transition settings
          | Days      | From     | ID               | Days active | Exclude Holidays    |
          | <days>    | <from>   | <transition_id>  | All         | <exclude holidays>  |
    And an enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "<policy>"
    Then "id" in "desiredPolicy" object of the device record is changed to "<policy>"
    And SCHEDULED POLICY CHANGE to "<transition_id>" policy is correctly set according to Transition config
  Examples:
    | days | from     | transition_id	 | exclude holidays | policy       | holiday  |
    | 1    | ASSIGNED | TEST_NOTIFICATION| Checked          | TEST_MESSAGE | tomorrow |
    | 1    | ASSIGNED | TEST_LOCK        | Checked          | TEST_MESSAGE | tomorrow |


  @ATP-1027 @ATP-1028 @ATP-1029 @ATP-765 @ATP-1034 @slow
  @env:local
  Scenario Outline: KNOX_GUARD | Automated Transition | from ASSIGNED "<initial policy>" policy to "<id>" policy
    Given an enrolled "KNOX_GUARD" device with "TEST_SHIPPED" policy
    And a "<initial policy>" policy with the Automated Transition settings
    | Days   | From   | ID    | Days active   | Exclude Holidays   |
    | <days> | <from> | <id>  | <days active> | <exclude holidays> |
    When a user changes policy via Admin Public API to "<initial policy>"
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "<id>"

  Examples:
    | initial policy | days | from      | id           | days active | exclude holidays |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_MESSAGE | All         | False            |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_BLINK   | All         | False            |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_LOCK    | today       | False            |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_LOCK    | All         | False            |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_MESSAGE | All         | False            |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_BLINK   | today       | False            |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_MESSAGE | All         | False            |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_BLINK   | All         | False            |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_LOCK    | today       | False            |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_RELEASE | All         | False            |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_RELEASE | today       | False            |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_RELEASE | All         | False            |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_RELEASE | today       | False            |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_RELEASE | All         | False            |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_RELEASE | today       | False            |


  @ATP-1027 @ATP-1028 @ATP-1029 @ATP-766 @ATP-1034 @slow
  @env:local
  Scenario Outline: KNOX_GUARD| Automated Transition | from ACTIVATED "<initial policy>" policy to "<id>" policy
    Given an enrolled "KNOX_GUARD" device with "TEST_SHIPPED" policy
    And a "<initial policy>" policy with the Automated Transition settings
      | Days   | From   | ID    | Days active   | Exclude Holidays   |
      | <days> | <from> | <id>  | <days active> | <exclude holidays> |
    When a user changes policy via Admin Public API to "<initial policy>"
    And "<initial policy>" policy is applied on device
    And it is the transition time in the interval set
    Then "id" in "desiredPolicy" object of the device record is changed to "<id>"

  Examples:
    | initial policy | days | from      | id           | days active | exclude holidays |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_MESSAGE | today       | False            |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_BLINK   | All         | False            |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_LOCK    | All         | False            |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_LOCK    | today       | False            |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_MESSAGE | All         | False            |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_BLINK   | All         | False            |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_MESSAGE | today       | False            |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_BLINK   | All         | False            |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_LOCK    | All         | False            |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_RELEASE | today       | False            |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_RELEASE | All         | False            |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_RELEASE | today       | False            |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_RELEASE | All         | False            |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_RELEASE | today       | False            |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_RELEASE | All         | False            |


  @ATP-1030 @ATP-1031 @ATP-1032 @ATP-1034 @slow
  @env:test4_qa
  Scenario Outline: KNOX_GUARD| Automated Transition | from ASSIGNED "<initial policy>" policy to "<id>" policy,
                    excluding holidays
    Given there are holiday configured for "<holiday>" for the admin account
    And an enrolled "KNOX_GUARD" device with "TEST_SHIPPED" policy
    And a "<initial policy>" policy with the Automated Transition settings
      | Days   | From   | ID    | Days active   | Exclude Holidays   |
      | <days> | <from> | <id>  | <days active> | <exclude holidays> |
    When a user changes policy via Admin Public API to "<initial policy>"
    Then "id" in "desiredPolicy" object of the device record is changed to "<initial policy>"
    And SCHEDULED POLICY CHANGE to "<id>" policy is correctly set according to Transition config

  Examples:
    | initial policy | days | from      | id           | days active | exclude holidays | holiday  |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_LOCK    | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_MESSAGE | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_BLINK   | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_MESSAGE | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_BLINK   | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_LOCK    | today       | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_MESSAGE | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_SHIPPED | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_LOCK    | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_LOCK    | today       | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ASSIGNED  | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ASSIGNED  | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ASSIGNED  | TEST_RELEASE | today       | Checked          | tomorrow |


  @ATP-1030 @ATP-1031 @ATP-1032 @ATP-1034 @slow
  @env:test4_qa
  Scenario Outline: KNOX_GUARD| Automated Transition | from ACTIVATED "<initial policy>" policy to "<id>" policy,
                    excluding holidays
    Given there are holiday configured for "<holiday>" for the admin account
    And an enrolled "KNOX_GUARD" device with "TEST_SHIPPED" policy
    And a "<initial policy>" policy with the Automated Transition settings
      | Days   | From   | ID    | Days active   | Exclude Holidays   |
      | <days> | <from> | <id>  | <days active> | <exclude holidays> |
    When a user changes policy via Admin Public API to "<initial policy>"
    And "<initial policy>" policy is applied on device
    Then "id" in "desiredPolicy" object of the device record is changed to "<initial policy>"
    And SCHEDULED POLICY CHANGE to "<id>" policy is correctly set according to Transition config

  Examples:
    | initial policy | days | from      | id           | days active | exclude holidays | holiday  |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_LOCK    | today       | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_MESSAGE | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_BLINK   | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_MESSAGE | today       | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_MESSAGE | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_BLINK   | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_LOCK    | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_BLINK   | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_MESSAGE | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_BLINK     | 1    | ACTIVATED | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_MESSAGE   | 1    | ACTIVATED | TEST_RELEASE | All         | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_RELEASE | today       | Checked          | tomorrow |
    | TEST_LOCK      | 1    | ACTIVATED | TEST_RELEASE | All         | Checked          | tomorrow |


  @ATP-683 @ATP-699 @ATP-726
  @env:local
  Scenario Outline: KNOX GUARD | Scheduled actions | STANDARD target type apply when Delayed "<policy>" is activated outside of\
    activation window
    Given a "<policy>" configured with delayed activation
      | repetitionInterval | assignedTimeBeforeActivationWindow | Days active | excludeHolidays |
      | 5h                 | True                               | All         | False           |
    And an enrolled "<provisioning>" device with "<initial policy>" policy
    And "<initial policy>" policy is applied on device
    When the "<policy>" has been applied but not yet activated
    Then "id" in "desiredPolicy" object of the device record is changed to "<policy>"
    And "lastCommandTargetType" is "<value>"
    And "nextActionDueTime" is equal to "start time"
    Examples:
      | initial policy | policy       | provisioning | value    |
      | TEST_LOCK      | TEST_MESSAGE | KNOX_GUARD   | STANDARD |
      | TEST_SHIPPED   | TEST_LOCK    | KNOX_GUARD   | STANDARD |
      | TEST_SHIPPED   | TEST_MESSAGE | KNOX_GUARD   | STANDARD |
      | TEST_SHIPPED   | TEST_BLINK   | KNOX_GUARD   | STANDARD |

  @ATP-697
  @env:test4_qa
  Scenario: KNOX GUARD | Scheduled action| Verify the nextActionDueTime set correctly with Holiday
    Given there are holiday configured for "tomorrow" for the admin account
    And a "TEST_MESSAGE" configured with delayed activation
      | repetitionInterval | assignedTimeBeforeActivationWindow | holiday  | excludeHolidays | Days active |
      | 1d                 | True                               | tomorrow | True		     | All         |
    And an enrolled "KNOX_GUARD" device with "TEST_SHIPPED" policy
    When a user changes policy via Admin Public API to "TEST_MESSAGE"
    And "TEST_MESSAGE" policy is applied on device
    Then "nextActionDueTime" is equal to "day after tomorrow + start time"


  @ATP-372
  @env:test4_qa
  Scenario: KG | Test the Public API client - getPin Endpoint
    Given An enrolled "KNOX_GUARD" device with "TEST_LOCK" policy
    When The user generated the pin via Admin Public API
    Then The "pin" should be successfully generated


  @ATP-229
  Scenario Outline: KG&ALPS | Test the Public API client - getStatus Endpoint
    Given an enrolled "<provisioning>" device with "TEST_SHIPPED" policy
    When The User searches for the imei of the device by calling the /status endpoint on the publicapi
    Then The response should return the correct imei and "assignedPolicy" should be None
    And The last checkin "lastCheckIn" time should be None

    Examples:
      | provisioning |
      | KNOX_GUARD   |
      | ALPS         |


  @ATP-511 @ATP-512
  Scenario Outline: KG&ALPS | Public API: Check Policy Application and Activation Time
    Given An enrolled "<provisioning>" device with "TEST_SHIPPED" policy
    And "TEST_SHIPPED" policy is applied on device
    When The User searches for the imei of the device by calling the /status endpoint on the publicapi
    Then Applied and activated time values are seen under "assignedPolicyAssignmentTime" and "assignedPolicyActivationTime" fields

    Examples:
      | provisioning |
      | ALPS         |
      | KNOX_GUARD   |


  @ATP-516
  Scenario: KG | Public API: Check deviceReady flag
    Given An enrolled "KNOX_GUARD" device with "TEST_SHIPPED" policy
    And "TEST_SHIPPED" policy is applied on device
    When The User searches for the imei of the device by calling the /status endpoint on the publicapi
    Then The "deviceReady" flag is seen


  @ATP-304
  Scenario: Register multiple valid and invalid IMEIs via Public API
    Given The New IMEI is valid and Policy is valid
      | IMEI | policy       |
      |      | TEST_SHIPPED |
    And The New IMEI is invalid and Policy is valid
      | IMEI            | policy       |
      | 111111112222222 | TEST_SHIPPED |
      | abcdefghijklmno | TEST_SHIPPED |
      | $%%^%^&%^&*     | TEST_SHIPPED |
    When The User registers the IMEIs via public API
    Then Errors will be displayed "Message" for the failed ones
      | IMEI            | Message            |
      | abcdefghijklmno | IMEI_INVALID       |
      | $%%^%^&%^&*     | IMEI_INVALID       |
      | 111111112222222 | TAC_NOT_AUTHORISED |


  @ATP-320
  Scenario: Update multiple valid and invalid IMEIs with valid and invalid policies via Public API
    Given The New IMEI is valid and Policy is valid
        | IMEI            | policy         |
        |                 | TEST_SHIPPED   |
    And The New IMEI is valid and Policy is invalid
        | IMEI            | policy         |
        |                 | INVALID_POLICY |
    And The New IMEI is invalid and Policy is valid
        | IMEI            | policy         |
        | abcdefghijklmno | TEST_SHIPPED   |
    And The New IMEI is invalid and Policy is invalid
        | IMEI            | policy         |
        | $%%^%^&%^&*     | INVALID_POLICY |
    And The Existing IMEI is valid and Policy is valid and New
        | IMEI            | policy         |
        |                 | TEST_MESSAGE   |
    And The Existing IMEI is valid and Policy is valid and Same
        | IMEI            | policy         |
        |                 | TEST_SHIPPED   |
    And The Existing IMEI is valid and Policy is invalid
        | IMEI            | policy         |
        |                 | INVALID_POLICY |
    When The User updates the IMEIs via public API
    Then Only the Valid existing IMEIs with the Valid Policies will be updated
    And Errors will be displayed "Message" for the failed ones


  @ATP-449
  Scenario: Public API: Update device with empty properties
    Given a MNO has the following custom properties assigned
      | estado  | codigoDePago  | montoDeDeuda |
      | Estado  | CodigoDePago  | MontoDeDeuda |
    And a user has already registered the below "ALPS" IMEI using following contents
      | imei            | policy       | estado        | codigoDePago | montoDeDeuda |
      | <random_imei>   | TEST_SHIPPED | Notificación  | 20110455     | S/241.00     |
    When the user Updates the device details of the following IMEI via public api
      | imei            | policy       | estado        | codigoDePago | montoDeDeuda |
      | <random_imei>   | TEST_BLINK   |               |              |              |
    Then the device is successfully updated
    And the custom property values for below is updated to "NULL"
      | estado | codigoDePago | monteDeDeuda |


  @ATP-448
  Scenario Outline: Public API: Update device with custom property value
    Given a MNO has the following custom properties assigned
      | estado  | codigoDePago  | montoDeDeuda |
      | Estado  | CodigoDePago  | MontoDeDeuda |
    And a user has already registered the below "<provisioning>" IMEI using following contents
      | imei            | policy       | estado       | codigoDePago | montoDeDeuda |
      | <random_imei>   | TEST_SHIPPED | Notificación | 20110455     | S/241.00     |
    When the user Updates the device details of the following IMEI via public api
      | imei            | policy       | estado                 |
      | <random_imei>   | TEST_SHIPPED | updated - Notificación |
    Then the device is successfully updated
    And the "estado" property value for the registered devices should be "updated - Notificación"
    But the "estado" property value for the MNO should be "Estado"
    And the property values for the below should not be changed
      | custom properties | custom values |
      | codigoDePago      | 20110455      |
      | montoDeDeuda      | S/241.00      |

    Examples:
      | provisioning |
      | KNOX_GUARD   |
      | ALPS         |


  @ATP-685 @slow
  @env:local
  Scenario: KG | ALPS-1232 | Scheduled actions | Getting the Repetition Message with delayed activation
    Given a "TEST_MESSAGE" configured with delayed activation
     | assignedTimeBeforeActivationWindow | delayInitialActivation | Days active | repetitionInterval |
     | False                              | True                   | All         | 5m                 |
    And an enrolled "KNOX_GUARD" device with "TEST_MESSAGE" policy
    When "TEST_MESSAGE" policy is applied on device
    Then "kgActionScheduling" object of the device record correspond to "<test policy>" settings
    And "nextActionDueTime" is equal to "repetition rate"


  @ATP-758 @ATP-759 @ATP-760
  Scenario Outline: Custom permissions are granted to Public API with generated JWT token
    Given a user generates JWT with "<permissions>" permission parameter
    And An admin has default custom properties defined
      | CustomProperty |
      | Property value |
    And An enrolled "ALPS" device with "TEST_SHIPPED" policy
    When a user makes a "<function>" call using generated JWT token
    Then a user is able "<able_to_call>" to make a "<function>" function call

    Examples:
      | permissions            | function          | able_to_call |
      | status                 | get_device_status | True         |
      | status                 | register_device   | False        |
      | status                 | generate_pin      | False        |
      | status                 | update_device     | False        |
      | register getpin        | get_device_status | False        |
      | register getpin        | register_device   | True         |
      | register getpin        | generate_pin      | True         |
      | register getpin        | update_device     | False        |
      | status register update | get_device_status | True         |
      | status register update | register_device   | True         |
      | status register update | generate_pin      | False        |
      | status register update | update_device     | True         |
