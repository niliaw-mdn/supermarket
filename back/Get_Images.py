# Alireza Samanipour
# Getting images from camera and saving in a directory using opencv-python lib
import cv2
import os

# Number of cameras
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to read camera feed!")

output_dir = 'back\Getting Images'
# os.makedirs(output_dir, exist_ok=True)
image_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Webcam', frame)
    k = cv2.waitKey(1)
    if k % 256 == 27:
        print("Escape hit, closing...") #break poin of while
        break
    elif k % 256 == ord('s'):   # wait for 's' key to save and exit
        img_name = os.path.join(output_dir, "opencv_frame_{}.png".format(image_counter))
        cv2.imwrite(img_name, frame)
        print("{}written!".format(img_name))
        image_counter += 1

cap.release()
cv2.destroyAllWindows()
