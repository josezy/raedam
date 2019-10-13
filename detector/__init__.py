import numpy as np

from mrcnn.model import MaskRCNN
from mrcnn.config import Config


LABELS_FILE = 'detector/train2_labels.txt'
WEIGHTS_FILE = 'detector/Train2.h5'  # Not included in repo

CLASS_NAMES = open(LABELS_FILE).read().strip().split("\n")


class SimpleConfig(Config):
    NAME = "coco_inference"
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    NUM_CLASSES = len(CLASS_NAMES)


def load_model():
    model = MaskRCNN(
        mode="inference",
        config=SimpleConfig(),
        model_dir='./model_logs'
    )
    model.load_weights(WEIGHTS_FILE, by_name=True)
    return model


def clean_boxes(r, class_names, score_threshold):
    boxes = r['rois']
    class_ids = r['class_ids']
    scores = r['scores']
    cleaned_boxes = []

    for i, box in enumerate(boxes):
        if scores[i] < score_threshold:

            continue

        cls_name = CLASS_NAMES[class_ids[i]]
        if cls_name in class_names:
            cleaned_boxes.append(box)

    return np.array(cleaned_boxes)
