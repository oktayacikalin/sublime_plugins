def view_is_too_big(view, max_size_setting, default_max_size=None):
    settings = view.settings()
    max_size = settings.get(max_size_setting, default_max_size)
    # print max_size, type(max_size)
    if max_size not in (None, False):
        max_size = long(max_size)
        cur_size = view.size()
        if cur_size > max_size:
            return True
    return False


def view_is_widget(view):
    settings = view.settings()
    return bool(settings.get('is_widget'))
