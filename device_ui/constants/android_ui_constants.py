import enum


class ALPSCONSTANTS(enum.Enum):
    PACKAGE = "com.trustonic.telecoms.standard.dpc"
    ROOT_CLASS = "android.widget.LinearLayout"  # TODO request an ID for this element from the dev team
    ACTION_BAR_ROOT = "com.trustonic.telecoms.standard.dpc:id/action_bar_root"
    ICON_HOME = "com.trustonic.telecoms.standard.dpc:id/nav_home"
    MESSAGE_TITLE = "payment__title"
    MESSAGE_TEXT = "payment__message"
    MAINTENANCE_CHECKIN = "com.trustonic.telecoms.standard.dpc:id/buttonCheckIn"


class KNOXGUARGCONSTANTS(enum.Enum):
    ROOT_CLASS = 'android.widget.FrameLayout'
    PACKAGE = 'com.samsung.android.kgclient'
    OK_BTN = 'com.samsung.android.kgclient:id/ok_btn'
    MESSAGE_TEXT = 'com.samsung.android.kgclient:id/message_tv'
    MESSAGE_TITLE = 'com.samsung.android.kgclient:id/company_tv'
    HOME_SCREEN = 'com.samsung.android.kgclient:id/info_layout'


class SETTINGS(enum.Enum):
    ADD_LANG = "com.android.settings:id/add_language"
    RECYCLER = "android.support.v7.widget.RecyclerView"
    SEARCH_INPUT = "android:id/search_src_text"
    LIST = "android:id/list"
    BUTTON_1 = "android:id/button1"
    BUTTON_2 = "android:id/button2"
    REGION_CURRENT = "com.android.settings:id/region_summary"
    BUTTON_REGION = "com.android.settings:id/region_title"
    LABEL = "com.android.settings:id/label"
    GEAR = "com.android.settings:id/gear"
