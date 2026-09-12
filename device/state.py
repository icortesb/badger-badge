import json
import os


def _copy(data):
    return json.loads(json.dumps(data))


def load(path, defaults):
    data = _copy(defaults)
    try:
        with open(path) as f:
            stored = json.load(f)
    except (OSError, ValueError):
        return data
    if not isinstance(stored, type(defaults)):
        return data
    if isinstance(defaults, dict):
        for key in defaults:
            if key in stored:
                data[key] = stored[key]
        return data
    return stored


def save(path, data):
    if "/" in path:
        try:
            os.mkdir(path.rsplit("/", 1)[0])
        except OSError:
            pass
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.rename(tmp, path)
