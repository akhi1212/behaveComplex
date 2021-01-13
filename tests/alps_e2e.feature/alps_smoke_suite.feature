@E2E_Tests @Regression_Tests @Smoke_Tests @ALPS_Client
@env:test4_qa
Feature: E2E smoke suite
  # Automated smoke suite ATP-989

  @ATP-425 @no_device
  Scenario: Register IMEIs - Upload csv file with custom properties
    Given An admin has default custom properties defined
       | Estado | CodigoDePago | MontoDeDeuda |
       | Estado | CodigoDePago | MontoDeDeuda |
    When a user belonging to MNO uploads a csv file to register using following contents
       | imei          | policy        | estado       | codigoDePago | montoDeDeuda |
       | <random_imei> | TEST_SHIPPED  | Notificación | 20110455     | S/241.00     |
       | <random_imei> | TEST_SHIPPED  | Notificación | 20110455     | S/241.00     |
    Then the file should be successfully uploaded into alps without any errors
    And the user should be able to search for the uploaded imei's and view the device details
    And the user should be able to view the following custom properties in device detail page
      | ESTADO       | CODIGODEPAGO | MONTODEDEUDA |
      | Notificación | 20110455     | S/241.00     |


  @ATP-978
  Scenario Outline: ALPS Client | Localised Lock screen
    Given a "TEST_LOCK" configured with next parameters
      | addLocaleOverridesTitle | Title        | localisedTitle   | addLocaleOverridesMsg | Message   | localisedMessage |
      | es                      | <titleText>  | <localisedTitle> | es                    | <msgText> | <localisedMsg>   |
    And the device is not registered in the system
    And the device configured with es language
    And a user belonging to MNO uploads a csv file to register using following contents
      | imei               | policy      |
      | <real_device_imei> | TEST_LOCK   |
    And the file should be successfully uploaded into alps without any errors
    And proceed with enrollment
    When the device is locked by policy with id TEST_LOCK within None seconds
    Then ALPS app takes the full screen
    And ALPS message with <localisedTitle> and <localisedMsg> is shown

    Examples:
    | titleText   | localisedTitle      | msgText               | localisedMsg          |
    | Lock policy | Politica de bloqueo | Standard notification | Notificacion estandar |


  @ATP-617 @no_device
  Scenario: ALPS Client | CSV Export | check policyAssignmentTime and policyActivationTime
    Given An admin has default custom properties defined
       | Estado | CodigoDePago | MontoDeDeuda |
       | Estado | CodigoDePago | MontoDeDeuda |
    When a user belonging to MNO uploads a csv file to register using following contents
       | imei          | policy       | estado       | codigoDePago | montoDeDeuda |
       | <random_imei> | TEST_MESSAGE | Notificación | 20110455     | S/241.00     |
    And user exports CSV report with "TEST_MESSAGE" policy
    Then exported CSV "TEST_MESSAGE" report file contains
      | policyAssignmentTime | policyActivationTime |
      | UNIX time            | UNIX time            |
