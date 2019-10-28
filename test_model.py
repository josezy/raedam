import os
import sys
import cv2
import django

from raedamdjango.cerebro import load_model, clean_boxes

sys.path.append("./raedamdjango/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from parking.models import ParkingCamera


CAM_SHORT_ID = 'b70e6965'

cam = ParkingCamera.objects.get(id__startswith=CAM_SHORT_ID)
cap = cv2.VideoCapture(cam.url)
success, frame = cap.read()
if not success:
    raise ValueError(f"[!] Cannot read from source '{cam.url}'")

rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

model = load_model()
r = model.detect([rgb_frame], verbose=0)[0]
cleaned_boxes = clean_boxes(r, ['car', 'bus', 'truck'], 0.8)
cam.spots = cleaned_boxes.tolist()
cam.save()

for box in cleaned_boxes:
    y1, x1, y2, x2 = box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

cv2.imwrite('data/pics/test.png', frame)
