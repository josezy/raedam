import cv2

from detector import load_model, clean_boxes


model = load_model()

cap = cv2.VideoCapture("http://75.147.0.206/mjpg/video.mjpg")
_, frame = cap.read()
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

r = model.detect([rgb_frame], verbose=0)[0]
cleaned_boxes = clean_boxes(r, ['car', 'bus', 'truck'], 0.8)
print(cleaned_boxes)

for box in cleaned_boxes:
    y1, x1, y2, x2 = box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

cv2.imwrite('pics/test.png', frame)
