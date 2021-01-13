def get_android_selector(**kwargs) -> str:
    selector = AndroidUiSelector(**kwargs)
    return str(selector)


class AndroidUiSelector:
    """
    Builds android UiSelector
        >>> selector = AndroidUiSelector(cls_name="some class name", text="some text", do_scroll=True)
        >>> str(selector)
        'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().className("some class name").text("some text"))'
    """
    def __init__(self, **params):
        self.params = params
        self.do_scroll = self.params.pop("do_scroll", True)
        self.new_scrollable = "new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({})"
        self.new_selector = "new UiSelector()"

        self.id_ = 'resourceId("{}")'
        self.cls_name = 'className("{}")'
        self.text = 'text("{}")'
        self.text_contains = 'textContains("{}")'
        self.descr = 'description("{}")'
        self.descr_contains = 'descriptionContains("{}")'

    def __str__(self):
        selector = self.new_selector
        for k, v in self.params.items():
            if v is not None:
                selector += "." + getattr(self, k).format(v)

        if self.do_scroll:
            selector = self.new_scrollable.format(selector)

        return selector
