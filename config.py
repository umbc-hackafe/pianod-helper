import json
import os

values = {}

def init():
    global values
    search_places = [os.environ.get("PIANOD_HELPER_CONF")]
    try:
        import xdg
        search_places.append(os.path.join(xdg.BaseDirectory.xdg_config_home, "pianod-helper.json"))
    except ImportError:
        pass
    search_places.append(os.path.join(os.path.expanduser("~"), ".pianod-helper.json"))
    search_places.append("/etc/pianod-helper.json")
    search_places.append(os.path.join(os.curdir, "config.json"))

    for loc in search_places:
        if loc:
            try:
                with open(loc) as source:
                    values = json.load(source)
                    break
            except IOError:
                pass
    else:
        raise FileNotFoundError("Config not found at any of: " + str([place for place in search_places if place]))

    if "pianod" not in values:
        values['pianod'] = {}

    block = values['pianod']
    if "host" not in block: block['host'] = "localhost"
    if "port" not in block: block['port'] = 4445
    if "user" not in block: block['user'] = "admin"
    if "pass" not in block: block['pass'] = "admin"

    if "ping" not in values:
        values['ping'] = {}

    block = values['ping']
    if "sleep" not in block: block['sleep'] = 60

    if "users" not in values:
        values['users'] = {}

def usernames():
    return values['users'].keys()

init()
