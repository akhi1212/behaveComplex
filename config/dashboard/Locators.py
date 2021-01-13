from selenium.webdriver.common.by import By


class Locators:
    # Login page
    login_username = (By.ID, "username")
    login_password = (By.ID, "password")
    login_btn = (By.ID, "kc-login")

    # dashboard top bar
    user_menu_btn = (By.XPATH, "//mno-popover[@triggericon='user']")
    user_name_in_menu = (By.CLASS_NAME, "topbar__username")
    topbar_trustonic = (By.CLASS_NAME, "topbar__brand")

    # dashboard device page
    device_tab = (By.XPATH, "//a[@href='/en/device']")
    search_device = (By.ID, "device-search-input deviceSearchInputTxt-at")
    device_summary_title = (By.CLASS_NAME, "summary__title")
    assign_policy_btn = (By.CLASS_NAME, "status__btn")
    policy_dropdown = (By.ID, "deviceStatus-at")
    save_policy_assign_btn = (By.ID, "saveDeviceStatusBtn-at")
    device_imei_at_summary = (By.ID, "deviceViewIMEITxt-at")
    device_properties_table = (By.XPATH, "//mno-tab[@id='devicePropertiesTab-at']//div[@class='device-properties']")
    current_policy = (By.ID, "currentPolicyName-at")

    # dashboard Policy page
    policies_tab = (By.XPATH, "//a[@href='/en/policies']//span[text()='Policies']")
    generate_pin_menu = (By.XPATH, "//mno-popover[@class='deviceMenu']//button[@type='button']")
    generate_pin_btn = (By.ID, "generate-pin")
    policies_header = (By.XPATH, "//header[@class='page-header']//mno-browser-title[contains(text(), 'Policies')]")
    policy_card = (By.XPATH, "//mno-card[@class='col-md-4 policy']")
    policy_change_btn = (By.XPATH, "//span[text()='Modify']")
    policy_definition = (By.XPATH, "//div[@class='card-body']//div[text()='Basic definition']")
    policy_id = "//div[@class='policy__id text-ellipsis']"

    # Add/update policy
    add_policy_btn = (By.ID, "addPolicyBtn-at")
    add_blank_policy = (By.ID, "blankPolicyBtn-at")
    policy_id_field = (By.ID, "editPolicyPolicyIdControl-at")
    policy_name_field = (By.XPATH, "//input[@formcontrolname='defaultValue']")
    alps_tab_policy = (By.XPATH, "//button[@class='tabs__button']//div[text()='ALPS']")
    alps_notification_type = (By.ID, "editPolicyAlpsNotificationTypeTxt-at")
    alps_lock = (By.XPATH, "//option[text()='Screen lock']")
    lock_title_field = (By.XPATH, "//mno-edit-message[@formcontrolname='screenLockTitle']//input")
    lock_message_field = (By.XPATH, "//mno-edit-message[@formcontrolname='screenLockMessage']//textarea")
    temporary = (By.ID, "editPolicyNonDismissibleTypeLbl-at")
    activation_duration = (By.XPATH, "//mno-duration[@id='editPolicyEnableActivationDurationTxt-atalps']//input")
    save_policy_btn = (By.ID, "policyEditSubmitBtn-at")

    # dashboard Import tab
    import_tab = (By.XPATH, "//a[@href='/en/device/import']")
    register_btn = (By.XPATH, "//button[@class='tabs__button']//div[text()='Register']")
    select_file_input = (By.ID, 'deviceUploadFile-at')
    upload_confirm_chkbox = (By.ID, 'deviceUploadConfirmLbl-at')
    upload_btn = (By.ID, 'uploadButton')
    upload_result_alert = (By.XPATH, "//div[@class='results']//div[@class='alert__text']")

    # dashboard Report tab
    report_tab = (By.XPATH, "//a[@href='/en/reports']")
    csv_download_button = (By.ID, "downloadDeviceReportCsvBtn-at")
    device_report_selector = (By.ID, "reportDeviceState-at")

    # Helpers
    @staticmethod
    def btn_on_device_tab(name):
        subtabs_on_device_tab = {
            "History": "History",
            "Info": "Info",
            "Properties": "Properties"
        }
        return By.XPATH, "//button[@class='tabs__button']//div[text()='%s']" % subtabs_on_device_tab[name]

    @staticmethod
    def btn_by_name_text(name):
        tabs = {
            "Devices": "Devices",
            "Import": "Import",
            "Reports": "Reports",
            "Policies": "Policies"
        }
        return By.XPATH, "//span[text()='%s']" % tabs[name]
