import combo

TABS = ("badge", "links", "projects")
TAB_BUTTONS = {"a": "badge", "b": "links", "c": "projects"}
DEFAULTS = {"tab": "badge", "link": 0, "project": 0, "combo": 0, "partials": 0}


def _int(value):
    if isinstance(value, int) and value >= 0:
        return value
    return 0


def handle(state, button, link_count, project_count):
    s = dict(DEFAULTS)
    s.update(state)
    if s["tab"] not in TABS:
        s["tab"] = "badge"
    for key in ("link", "project", "combo", "partials"):
        s[key] = _int(s[key])

    s["combo"], completed = combo.advance(s["combo"], button)

    if button in TAB_BUTTONS:
        s["tab"] = TAB_BUTTONS[button]
    elif button in ("up", "down"):
        step = -1 if button == "up" else 1
        if s["tab"] == "links" and link_count:
            s["link"] += step
        elif s["tab"] == "projects" and project_count:
            s["project"] += step

    if link_count:
        s["link"] %= link_count
    if project_count:
        s["project"] %= project_count
    return s, ("quiz" if completed else None)
