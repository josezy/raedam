import cv2
import json
import tensorflow as tf

from flask import Flask, render_template, jsonify, redirect, request
from decimal import Decimal

from detector import load_model
from util import coords_in_radius


VIDEO_SOURCES_RADIUS = 500
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

app.model = load_model()
app.graph = tf.get_default_graph()


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

    print(f"[+] Getting closest cameras to point ({lat}, {lng})")
    closest_sources = [
        source for source in VIDEO_SOURCES
        if coords_in_radius(
            source['coords'],
            [lng, lat],
            VIDEO_SOURCES_RADIUS
        )
    ][:1]  # Hard limit number of detections

    print(f"[+] Getting frames for {len(closest_sources)} cameras")
    frames = []
    for source in closest_sources:
        cap = cv2.VideoCapture(source['url'])
        _, frame = cap.read()
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    print(f"[+] Performing detection for {len(closest_sources)} cameras")
    assert len(frames) == 1, 'Multiple frame detection not implemented yet'
    with app.graph.as_default():
        r = app.model.detect(frames, verbose=0)[0]

    print(r)
    # load pre marked spots for every zone and check for free spots
    # overlaps = mrcnn.utils.compute_overlaps(car_boxes, parking_areas)
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
    print("[i] Server up and running...")
    app.run()
