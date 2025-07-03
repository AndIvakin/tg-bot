import json, os

BASE = os.path.dirname(__file__)
SLOTS_FILE = os.path.join(BASE, 'slots.json')
ADMINS_FILE = os.path.join(BASE, 'admins.json')

def load_json(f, default):
    try: return json.load(open(f))
    except: return default

def save_json(f, data):
    json.dump(data, open(f, 'w'), indent=2)

def get_slots():
    return load_json(SLOTS_FILE, {})

def save_slots(s): save_json(SLOTS_FILE, s)

def get_admins():
    return load_json(ADMINS_FILE, [])

def add_admin(uid):
    admins = get_admins()
    if uid not in admins:
        admins.append(uid)
        save_json(ADMINS_FILE, admins)

def is_admin(uid):
    return uid in get_admins()
