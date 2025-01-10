# methods.py
import cv2
import threading
import supervision as sv
from ultralytics import YOLO
import time
import queue
from concurrent.futures import ThreadPoolExecutor

model = YOLO('best.pt')
box_annotator = sv.BoxAnnotator()
labels_annotator = sv.LabelAnnotator()
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Unable to read camera feed!")

stop_camera = False
start_time = time.time()
detection_counts = {}
frame_queue = queue.Queue(maxsize=10)
executor = ThreadPoolExecutor(max_workers=8)  # Adjust max_workers based on hardware

def process_frame(frame):
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    class_names = results.names

    global detection_counts
    latest_detections = [{'label': class_names[class_id], 'confidence': confidence} 
                            for class_id, confidence in zip(detections.class_id, detections.confidence)]
    for detection in latest_detections:
        label = detection['label']
        detection_counts[label] = detection_counts.get(label, 0) + 1

    return frame, detections

def enqueue_frame(frame):
    if not frame_queue.full():
        frame_queue.put(frame)

def dequeue_frame():
    try:
        return frame_queue.get_nowait()
    except queue.Empty:
        return None

def generate_frames():
    global stop_camera, start_time

    while True:
        if stop_camera or (time.time() - start_time > 20):  
            print("Stopping the camera after 20 seconds...")
            break

        success, frame = camera.read()
        if not success:
            continue

        frame = cv2.resize(frame, (640, 480)) 

        enqueue_frame(frame)
        frame = dequeue_frame()

        if frame is not None:
            future = executor.submit(process_frame, frame)
            frame, detections = future.result()

            annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=detections)
            annotated_frame = labels_annotator.annotate(scene=annotated_frame, detections=detections)

            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.01)  

    camera.release()
    most_detected_label = max(detection_counts, key=detection_counts.get, default=None)
    if most_detected_label is None:
        print(f"No detections made.")
    else:
        print(f"Most detected label: {most_detected_label}")
