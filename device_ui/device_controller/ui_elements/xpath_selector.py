XPATH_SWITCH = '//android.support.v7.widget.RecyclerView//android.widget.TextView[@text="{text}"]{parent_step}{child_step}'


def get_parent_last_child_xpath(from_el_with_text: str, parent_step: int = 0, child_step: int = 0) -> str:
    parent_xpath = "/parent::*"
    last_child_xpath = "/*[last()]"
    xpath = XPATH_SWITCH.format(
        parent_step=parent_xpath * parent_step,
        text=from_el_with_text,
        child_step=last_child_xpath * child_step
    )
    return xpath
