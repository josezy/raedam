import json

from flask import Flask, render_template, jsonify, redirect, request
from decimal import Decimal

from detector import load_model


VIDEO_SOURCES = [
    {
        'name': "Parking 1",
        'coords': [Decimal('-75.378882'), Decimal('6.146590')],  # San Nicolas
        'url': "http://199.48.198.27/mjpg/video.mjpg"
    },
    # {
    #     'name': "Parking Huge",
    #     'coords': [Decimal('-75.378855'), Decimal('6.148160')],  # Exito
    #     'url': "http://46.186.121.222:83/GetData.cgi"
    # },
    {
        'name': "Parking River",
        'coords': [Decimal('-75.389125'), Decimal('6.146871')],  # 6ta etapa
        'url': "http://75.147.0.206/mjpg/video.mjpg"
    },
    {
        'name': "Good Parking Canada",
        'coords': [Decimal('-75.389356'), Decimal('6.147737')],  # Iglesia
        'url': "http://192.75.71.26/mjpg/video.mjpg"
    },
]


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
    lng = Decimal(request.args.get('longitude'))
    print(lng, lat)

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


print("[i] Server up and running...")
if __name__ == '__main__':
    app.run()
