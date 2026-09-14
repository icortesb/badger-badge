import os


def remove_tree(path):
    for entry in list(os.ilistdir(path)):
        name, kind = entry[0], entry[1]
        if path == "/" and name == "data":
            continue
        full = path.rstrip("/") + "/" + name
        if kind == 0x4000:
            remove_tree(full)
            os.rmdir(full)
        else:
            os.remove(full)


remove_tree("/")
print("wiped (data kept)")
