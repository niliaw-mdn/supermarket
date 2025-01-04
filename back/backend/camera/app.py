from flask import Flask, render_template, Response, jsonify
import cv2
import os
import threading
import supervision as sv
from ultralytics import YOLO
import time

app = Flask(__name__)

model = YOLO('best.pt')
Box_Annotator = sv.BoxAnnotator()
labels_annotator = sv.LabelAnnotator()

camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Unable to read camera feed!")

# Global variable to store detection results
latest_detections = []
detection_counts = {}
stop_camera = False  # Flag to stop the camera
start_time = time.time()

def generate_frames():
    global latest_detections, detection_counts, stop_camera, start_time

    while True:
        if stop_camera or (time.time() - start_time > 10):  # Run for 5 seconds
            print("Stopping the camera after 5 seconds...")
            break

        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.resize(frame, (640, 480))  # Reduce resolution
            
            # Detect objects
            results = model(frame)[0]
            detections = sv.Detections.from_ultralytics(results)
            
            # Get class names
            class_names = results.names
            
            # Update the global detection results
            latest_detections = [{'label': detection[0], 'confidence': detection[1]} for detection in zip(detections.class_id, detections.confidence)]
            print(f"Latest detections: {latest_detections}")
            
            # Count detections
            for detection in latest_detections:
                label = detection['label']
                if label in detection_counts:
                    detection_counts[label] += 1
                else:
                    detection_counts[label] = 1
            print(f"Detection counts: {detection_counts}")

            # Annotate frame
            annotated_image = Box_Annotator.annotate(scene=frame.copy(), detections=detections)
            annotated_image = labels_annotator.annotate(scene=annotated_image, detections=detections)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_image)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Stop the camera
    camera.release()
    most_detected_label = class_names[ max(detection_counts, key=detection_counts.get, default=None)]
    print(f"Most detected label: {most_detected_label}")  # Print the most detected label
    return most_detected_label

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def detections():
    most_detected_label = generate_frames()  # Get the most detected label
    return jsonify({'most_detected': most_detected_label})

if __name__ == "__main__":
    threading.Thread(target=generate_frames).start()

    app.run(debug=True, threaded=True)
    #app.run(debug=True)


"""def simple_generate_frames():
    while True:
            
        ## read the camera frame
        success,frame = camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
"""