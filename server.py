#!/usr/bin/env python3

import json

from decimal import Decimal

from flask import Flask, render_template, jsonify, redirect, request
from util import load_json_file
from detector import load_model


# Config
app = Flask(__name__)
CONFIG_FILE = 'config.json'
SPOTS_FILE = 'spots.json'


def load_config(fname=CONFIG_FILE):
    """read the config.json file and load it as a dictionary"""
    with open(fname, 'r') as f:
        return json.load(f)


CONFIG = load_config(CONFIG_FILE)

model = load_model()


# Routes
@app.route('/favicon.ico')
def favicon():
    return redirect("/static/favicon.ico")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', **CONFIG)


@app.route('/zones', methods=['GET'])
def zones_data():
    lat = Decimal(request.args.get('latitude'))
    lon = Decimal(request.args.get('longitude'))
    print(lat, lon)
    # TODO
    # Get closest cameras (stream link)
    # for every camera in the range
    # grab a frame, detect free spots (based on marked spots)
    # build and return json with data
    return jsonify([
        {
            'coords': [-75.378855, 6.148160],
            'free_spots': 13,
            'total_spots': 15,
        },
        {
            'coords': [-75.378721, 6.148259],
            'free_spots': 5,
            'total_spots': 18,
        }
    ])


if __name__ == '__main__':
    app.run()
