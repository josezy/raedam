#!/usr/bin/env python3

import json

from flask import Flask, render_template, jsonify, redirect


# Config
app = Flask(__name__)
CONFIG_FILE = 'config.json'


def load_config(fname=CONFIG_FILE):
    """read the config.json file and load it as a dictionary"""
    with open(fname, 'r') as f:
        return json.load(f)


CONFIG = load_config(CONFIG_FILE)


# Routes
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', **CONFIG)


@app.route('/spots', methods=['GET'])
def available_spots():
    spots = [
        {
            'id': 1234,
            'free': True,
            'coords': [-75.378102, 6.149930],
        },
        {
            'id': 1235,
            'free': False,
            'coords': [-75.378106, 6.149850]
        }
    ]
    return jsonify(spots)


@app.route('/favicon.ico')
def favicon():
    return redirect("/static/favicon.ico")


if __name__ == '__main__':
    app.run()
