#!/usr/bin/env python3

import json
import random

from flask import Flask, render_template, jsonify, redirect, abort
from util import load_json_file, save_json_file, parse_coords


# Config
app = Flask(__name__)
CONFIG_FILE = 'config.json'
SPOTS_FILE = 'spots.json'


def load_config(fname=CONFIG_FILE):
    """read the config.json file and load it as a dictionary"""
    with open(fname, 'r') as f:
        return json.load(f)


CONFIG = load_config(CONFIG_FILE)


# Routes
@app.route('/favicon.ico')
def favicon():
    return redirect("/static/favicon.ico")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', **CONFIG)


@app.route('/spots', methods=['GET'])
def available_spots():
    spots = load_json_file(SPOTS_FILE)
    return jsonify(spots)


@app.route('/spot/register/<coords>', methods=['POST'])
def register_spot(coords):
    try:
        lon, lat = parse_coords(coords)
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Could not parse coordinates'
        })

    spots = load_json_file(SPOTS_FILE)
    spot_ids = [spot['id'] for spot in spots]

    try:
        new_id = random.choice(list(set(range(1000, 10000)) - set(spot_ids)))
    except IndexError:
        return jsonify({
            'success': False,
            'message': 'Could not assign an ID'
        })

    spots = spots + [{
        'id': new_id,
        'free': True,
        'coords': [lon, lat]
    }]

    save_json_file(SPOTS_FILE, spots)
    return jsonify({'success': True})


@app.route('/spot/delete/<int:spot_id>', methods=['POST'])
def delete_spot(spot_id):
    spots = load_json_file(SPOTS_FILE)
    updated_spots = [spot for spot in spots if spot['id'] != spot_id]
    save_json_file(SPOTS_FILE, updated_spots)
    return jsonify({'success': True})


@app.route('/spot/<int:spot_id>/<state>', methods=['POST'])
def update_spot(spot_id, state):
    if state not in ['free', 'busy']:
        abort(404)

    spots = load_json_file(SPOTS_FILE)
    matches = [spot for spot in spots if spot['id'] == spot_id]
    if len(matches) != 1:
        abort(404)

    matches[0]['free'] = True if state == 'free' else False
    updated_spot = matches[0]
    updated_spots = [
        updated_spot if spot['id'] == spot_id else spot
        for spot in spots
    ]
    save_json_file(SPOTS_FILE, updated_spots)

    return jsonify({'success': True})


@app.route('/spot/<int:spot_id>', methods=['POST'])
def spot_state(spot_id):
    spots = load_json_file(SPOTS_FILE)
    matches = [spot for spot in spots if spot['id'] == spot_id]
    if len(matches) != 1:
        abort(404)
    return jsonify(matches[0])


if __name__ == '__main__':
    app.run()
