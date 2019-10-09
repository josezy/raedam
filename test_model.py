import cv2

from detector import load_model, CLASS_NAMES
from mrcnn import visualize


model = load_model()

cap = cv2.VideoCapture("/Users/joseb/raedam/pics/river_busy.png")
_, frame = cap.read()
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

r = model.detect([rgb_frame], verbose=0)[0]

visualize.display_instances(
    rgb_frame, r['rois'], r['masks'], r['class_ids'], CLASS_NAMES, r['scores'])
