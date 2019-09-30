from mrcnn.model import MaskRCNN
from mrcnn.config import Config


LABELS_FILE = 'detector/coco_labels.txt'
WEIGHTS_FILE = 'detector/mask_rcnn_coco.h5'  # Not included in repo

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
