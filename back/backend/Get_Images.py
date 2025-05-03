import cv2
import os

# ایجاد پوشه برای ذخیره تصاویر در کنار همین فایل
output_dir = 'new_product_img'
os.makedirs(output_dir, exist_ok=True)

# باز کردن دوربین
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to access the camera!")
    exit()

image_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame!")
        break

    cv2.imshow('Webcam', frame)
    k = cv2.waitKey(1)

    if k % 256 == 27:  # ESC برای خروج
        print("Escape hit, closing...")
        break
    elif k % 256 == ord('s'):  # ذخیره عکس با زدن کلید 's'
        img_name = os.path.join(output_dir, f"opencv_frame_{image_counter}.png")
        cv2.imwrite(img_name, frame)
        print(f"Image {img_name} saved successfully!")
        image_counter += 1

cap.release()
cv2.destroyAllWindows()