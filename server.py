import cv2
import json
import mrcnn
import numpy as np
import tensorflow as tf

from flask import Flask, render_template, jsonify, redirect, request
from flask.json import JSONEncoder
from decimal import Decimal

from detector import load_model, clean_boxes
from util import coords_in_radius


CAR_SCORE = 0.8
CAR_CLS_NAMES = ['car', 'bus', 'truck']
VIDEO_SOURCES_RADIUS = 1000
VIDEO_SOURCES_DATA = [
    {
        'id': 1,
        'name': "parking_1",
        'coords': [Decimal('-75.378882'), Decimal('6.146590')],  # San Nicolas
        'url': "http://199.48.198.27/mjpg/video.mjpg"
    },
    # {
    #     'name': "Parking Huge",
    #     'coords': [Decimal('-75.378855'), Decimal('6.148160')],  # Exito
    #     'url': "http://46.186.121.222:83/GetData.cgi"
    # },
    {
        'id': 2,
        'name': "parking_river",
        'coords': [Decimal('-75.389125'), Decimal('6.146871')],  # 6ta etapa
        'url': "http://75.147.0.206/mjpg/video.mjpg"
    },
    {
        'id': 3,
        'name': "good_parking_canada",
        'coords': [Decimal('-75.389356'), Decimal('6.147737')],  # Iglesia
        'url': "http://192.75.71.26/mjpg/video.mjpg"
    },
]


class ExtendedEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, Decimal):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


# Config
app = Flask(__name__)
app.json_encoder = ExtendedEncoder
CONFIG_FILE = 'config.json'
SPOTS_FILE = 'spots.json'


def load_config(fname=CONFIG_FILE):
    """read the config.json file and load it as a dictionary"""
    with open(fname, 'r') as f:
        return json.load(f)


CONFIG = load_config(CONFIG_FILE)
ALL_SPOTS = load_config(SPOTS_FILE)

VIDEO_SOURCES = []
for src in VIDEO_SOURCES_DATA:
    if src['name'] in ALL_SPOTS:
        src_data = src
        src_data['spots'] = ALL_SPOTS[src['name']]
        VIDEO_SOURCES.append(src_data)


app.model = load_model()
app.graph = tf.get_default_graph()


# Routes
@app.route('/favicon.ico')
def favicon():
    return redirect("/static/favicon.ico")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', **CONFIG)

@app.route('/GetCamLocation', methods=['GET'])
def cam_location():
    return jsonify(VIDEO_SOURCES_DATA)


@app.route('/zones', methods=['GET'])
def zones_data():
    lat = Decimal(request.args.get('latitude'))
    lng = Decimal(request.args.get('longitude'))
    print(f"LATITUDE: {lat}, LONGITUDE: {lng}")
    closest_sources = [
        source for source in VIDEO_SOURCES

        if coords_in_radius(
            source['coords'],
            [lng, lat],
            VIDEO_SOURCES_RADIUS
        )
    ][:1]  # Hard limit number of detections
    print(closest_sources)
    assert len(closest_sources) == 1,\
        f'Multiple frame detection not implemented yet, there are {closest_sources} zones near'

    parking_data = []
    for source in closest_sources:
        cap = cv2.VideoCapture(source['url'])
        success, frame = cap.read()
        if not success:
            continue

        print(f"[+] Performing detection for source '{source['name']}'")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with app.graph.as_default():
            results = app.model.detect([rgb_frame], verbose=0)

        car_boxes = clean_boxes(results[0], CAR_CLS_NAMES, CAR_SCORE)
        car_spots = np.array(source['spots'])
        overlaps = mrcnn.utils.compute_overlaps(car_spots, car_boxes)

        for car_box in car_boxes:  # Detected cars
            y1, x1, y2, x2 = car_box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

        source_spots = {
            'id': source['id'],
            'coords': source['coords'],
            'total_spots': len(source['spots']),
            'free_spots': 0
        }
        for car_spot, overlap_areas in zip(car_spots, overlaps):  # Car spots
            y1, x1, y2, x2 = car_spot
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            radius = int((y2 - y1) / 2)
            free_spot = np.max(overlap_areas) < 0.2
            color = (0, 255, 0) if free_spot else (0, 0, 255)
            source_spots['free_spots'] += 1 if free_spot else 0
            cv2.circle(frame, center, radius, color, 3)

        assert source_spots['free_spots'] <= source_spots['total_spots'],\
            f"'free_spots' ({source_spots['free_spots']}) can't never "\
            f"be greater thatn 'total_spots' ({source_spots['total_spots']})"
        parking_data.append(source_spots)
        cv2.imwrite(f"pics/{source['name']}.png", frame)
    print("ES ESTE\n")
    print(jsonify(parking_data))
    return jsonify(parking_data)


if __name__ == '__main__':
    print("[i] Server up and running...")
    app.run()
