#!/usr/bin/env python3

# import sys
# import json
# from datetime import datetime

from flask import Flask, render_template#, redirect


### Config
app = Flask(__name__)
# CONFIG_FILE = 'content.json'
# HOST = 'http://127.0.0.1:5000'

# def load_config(fname=CONFIG_FILE):
#     """read the content.json file and load it as a dictionary"""
#     with open(fname, 'r') as f:
#         return json.load(f)

# CONFIG = load_config(CONFIG_FILE)

# PAGES = {page['url']: page for page in  list(CONFIG['PAGES'].values())}  # {url: {page_data}}
# POSTS = {post['url']: post for post in  list(CONFIG['POSTS'].values())}  # {url: {post_data}}


### Routes

@app.route('/')
def index():
    # return redirect("/index.html")
    return render_template('index.html')

# @app.route('/favicon.ico')
# def favicon():
#     return redirect("/static/favicon.ico")

# @app.route('/<path>')
# def render_page(path):
#     page = PAGES[f'/{path}']
#     return render_template(page['template'], now=datetime.now(), **CONFIG, **page)

# @app.route('/posts/<path>')
# def render_post(path):
#     print(path)
#     post = POSTS[f'/posts/{path}']
#     return render_template('post.html', now=datetime.now(), **CONFIG, **post)


if __name__ == '__main__':
    app.run()
