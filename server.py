#!/usr/bin/env python3

# import sys
import json
# from datetime import datetime

from flask import Flask, render_template, jsonify


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
            'name': "Spot 1",
            'free': True,
            'coords': [-75.378102, 6.149930],
        },
        {
            'name': "Spot 2",
            'free': False,
            'coords': [-75.378106, 6.149850]
        }
    ]
    return jsonify(spots)

# @app.route('/favicon.ico')
# def favicon():
#     return redirect("/static/favicon.ico")

# @app.route('/<path>')
# def render_page(path):
#     page = PAGES[f'/{path}']
#     return render_template(
#         page['template'],
#         now=datetime.now(),
#         **CONFIG,
#         **page
#     )

# @app.route('/posts/<path>')
# def render_post(path):
#     print(path)
#     post = POSTS[f'/posts/{path}']
#     return render_template('post.html', now=datetime.now(), **CONFIG, **post)


if __name__ == '__main__':
    app.run()
