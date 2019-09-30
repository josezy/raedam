from mrcnn.model import MaskRCNN
from mrcnn.config import Config


LABELS_FILE = 'detector/coco_labels.txt'
WEIGHTS_FILE = 'detector/mask_rcnn_coco.h5'  # Not included in repo

CLASS_NAMES = open(LABELS_FILE).read().strip().split("\n")


def load_model():
    config = Config()
    config.NAME = "coco_inference"
    config.IMAGES_PER_GPU = 1
    config.NUM_CLASSES = len(CLASS_NAMES)

    model = MaskRCNN(mode="inference", config=config, model_dir='./model_logs')
    model.load_weights(WEIGHTS_FILE, by_name=True)
    return model
