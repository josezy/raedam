import os
import json


def append_json_file(filepath, new_data):
    data_collected = load_json_file(filepath)
    data_collected.append(new_data)
    save_json_file(filepath, data_collected)


def save_json_file(filepath, json_data):
    with open(filepath, 'w') as fp:
        json.dump(json_data, fp)


def load_json_file(filepath):
    if not os.path.isfile(filepath):
        with open(filepath, 'w+') as fp:
            json.dump({}, fp)
        return {}

    with open(filepath, 'r+') as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError:
            fp.truncate(0)
            json.dump({}, fp)
            data = {}
    return data


def parse_coords(coords):
    _coords = "".join(coords.split()).split(',')
    if len(_coords) != 2:
        raise ValueError(
            f"Coordinates format is 'xx.xxxx,yy.yyyy'. Got '{coords}' instead"
        )
    return float(_coords[0]), float(_coords[1])
