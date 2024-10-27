# Alireza Samanipour
# 

import os
import cv2
import supervision as sv
from ultralytics import YOLO


model = YOLO(f'best.pt')

Bounding_Box_Annotator = sv.BoundingBoxAnnotator()
labels_annotator = sv.LabelAnnotator()


# Number of cameras
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to read camera feed!")

image_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)

    annotated_image = Bounding_Box_Annotator.annotate(scene=frame.copy(), detections=detections)
    annotated_image = labels_annotator.annotate(scene=annotated_image, detections=detections)
    
    cv2.imshow('Webcam', annotated_image)
    k = cv2.waitKey(1)
    if k % 256 == 27:
        print("Escape hit, closing...") #break poin of while
        break


cap.release()
cv2.destroyAllWindows()
