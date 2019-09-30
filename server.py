#!/usr/bin/env python3

import json

from flask import Flask, render_template, jsonify, redirect
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


@app.route('/spots', methods=['GET'])
def available_spots():
    spots = load_json_file(SPOTS_FILE)
    return jsonify(spots)


if __name__ == '__main__':
    app.run()
