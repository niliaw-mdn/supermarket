import os
import cv2
import streamlit as st
from ultralytics import YOLO
import torch
import json
import re
import math
from streamlit_autorefresh import st_autorefresh



# غیرفعال کردن watcher استریملت (برای جلوگیری از برخی ارور‌های torch)
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

# تعیین دستگاه: استفاده از GPU (cuda:0) در صورت موجود بودن
device = "cuda:0" if torch.cuda.is_available() else "cpu"
st.write(f"Running on device: {device}")

# بارگذاری مدل YOLO روی دستگاه مشخص‌شده (GPU یا CPU)
yolo = YOLO('best.pt', device=device)

# تنظیمات مربوط به ردیابی اشیاء
MISS_THRESHOLD = 3  # تعداد فریم‌هایی که شیء نباید دیده شود تا ردیابی آن خاتمه یابد

def initialize_session():
    if "detected_objects" not in st.session_state:
        st.session_state.detected_objects = {}  # دیکشنری نهایی محصولات
    if "tracks" not in st.session_state:
        st.session_state.tracks = []  # لیست اشیاء در حال ردیابی
    if "stop_processing" not in st.session_state:
        st.session_state.stop_processing = False
    if "purchase_submitted" not in st.session_state:
        st.session_state.purchase_submitted = False
    if "frame" not in st.session_state:
        st.session_state.frame = None
    if "camera" not in st.session_state:
        st.session_state.camera = None
    if "phone_number" not in st.session_state:
        st.session_state.phone_number = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "input"  # حالت‌های ممکن: "input" یا "operation"

def add_custom_css():
    st.markdown(
        """
        <style>
        body {
            font-family: 'IRANSans', sans-serif;
            background-color: #e8f5e9;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'IRANSans', sans-serif;
            font-size: 26px;
            color: #2e7d32;
        }
        .stTextArea>div>textarea {
            font-size: 18px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            font-size: 20px;
            padding: 15px 30px;
            margin: 15px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .reset-button>button, .submit-button>button {
            background-color: #FF5733;
            color: white;
            border-radius: 8px;
            font-size: 20px;
            padding: 15px 30px;
        }
        .reset-button>button:hover, .submit-button>button:hover {
            background-color: #E63939;
        }
        div.stMarkdown > div {
            font-size: 20px;
            line-height: 1.8;
        }
        .stDataFrame {
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def validate_phone_number(phone):
    pattern = r"^09\d{9}$"  # الگوی پیشنهادی برای شماره تماس
    return re.match(pattern, phone)

def update_tracks(detections):
    tracks = st.session_state.tracks
    for track in tracks:
        track["updated"] = False

    threshold_distance = 50  # آستانه فاصله (بر حسب پیکسل)

    for detection in detections:
        d_bbox = detection["bbox"]
        d_center = ((d_bbox[0] + d_bbox[2]) / 2, (d_bbox[1] + d_bbox[3]) / 2)
        best_match = None
        best_distance = threshold_distance
        for track in tracks:
            t_bbox = track["bbox"]
            t_center = ((t_bbox[0] + t_bbox[2]) / 2, (t_bbox[1] + t_bbox[3]) / 2)
            dist = math.sqrt((d_center[0] - t_center[0])**2 + (d_center[1] - t_center[1])**2)
            if dist < best_distance:
                best_distance = dist
                best_match = track
        if best_match is not None:
            best_match["bbox"] = d_bbox
            best_match["labels"].append(detection["label"])
            best_match["missed"] = 0
            best_match["updated"] = True
        else:
            new_track = {
                "bbox": d_bbox,
                "labels": [detection["label"]],
                "missed": 0,
                "updated": True
            }
            tracks.append(new_track)

    removal_list = []
    for track in tracks:
        if not track.get("updated", False):
            track["missed"] += 1
        if track["missed"] >= MISS_THRESHOLD:
            most_common_label = max(set(track["labels"]), key=track["labels"].count)
            st.session_state.detected_objects[most_common_label] = st.session_state.detected_objects.get(most_common_label, 0) + 1
            removal_list.append(track)
    for track in removal_list:
        if track in tracks:
            tracks.remove(track)

def process_new_frame():
    cap = st.session_state.camera
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 60)
        st.session_state.camera = cap

    ret, frame = cap.read()
    if not ret:
        st.warning("⚠️ عدم دریافت فریم از وب‌کم!")
        st.session_state.stop_processing = True
        return

    results = yolo(frame, imgsz=640)
    detections = []
    for result in results:
        boxes = result.boxes
        names = result.names
        for box in boxes:
            coords = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
            label = names[int(box.cls)]
            detections.append({"bbox": coords, "label": label})
            x1, y1, x2, y2 = map(int, coords)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    update_tracks(detections)
    st.session_state.frame = frame

def show_final_list():
    st.subheader("🛠️ لیست نهایی اشیاء شناسایی‌شده:")
    detected_objects = st.session_state.detected_objects

    for obj, count in list(detected_objects.items()):
        cols = st.columns([1, 1, 5])
        with cols[0]:
            if st.button("➕", key=f"increase_{obj}"):
                detected_objects[obj] += 1
        with cols[1]:
            if st.button("➖", key=f"decrease_{obj}"):
                detected_objects[obj] = max(0, detected_objects[obj] - 1)
        with cols[2]:
            st.write(f"**{obj}**: {detected_objects[obj]} بار")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.button("📦 ثبت خرید", key="submit_purchase"):
        st.session_state.purchase_submitted = True
        filtered_data = {k: v for k, v in detected_objects.items() if v > 0}
        purchase_data = {
            "phone_number": st.session_state.phone_number,
            "products": filtered_data
        }
        purchase_data_json = json.dumps(purchase_data, ensure_ascii=False, indent=2)
        st.text_area("🔗 داده‌های ارسال‌شده (JSON):", purchase_data_json, height=250)
        st.success("✅ خرید ثبت شد! برنامه متوقف می‌شود.")
        st.session_state.stop_processing = True
        if st.session_state.camera:
            st.session_state.camera.release()
            st.session_state.camera = None
        st.stop()
    
    if st.button("🔄 شروع دوباره", key="reset_button"):
        st.session_state.detected_objects = {}
        st.session_state.tracks = []
        st.session_state.stop_processing = False
        st.session_state.purchase_submitted = False
        if st.session_state.camera:
            st.session_state.camera.release()
        st.session_state.camera = None
        st.session_state.current_page = "input"
        st.stop()

def streamlit_app():
    st.set_page_config(page_title="شناسایی اشیاء", layout="wide")
    initialize_session()
    add_custom_css()
    
    # صفحه ورود شماره تماس
    if st.session_state.current_page == "input":
        st.title("ورود شماره تماس")
        st.session_state.phone_number = st.text_input("شماره تماس خود را وارد کنید:", value=st.session_state.phone_number)
        if st.session_state.phone_number.strip() != "":
            if not validate_phone_number(st.session_state.phone_number.strip()):
                st.error("⚠️ شماره تماس وارد شده معتبر نیست. لطفاً از فرمت صحیح (مثلاً: 09123456789) استفاده کنید.")
            else:
                if st.button("🎥 شروع عملیات"):
                    st.session_state.current_page = "operation"
                    st.session_state.stop_processing = False
                    st.stop()
        else:
            st.info("لطفاً شماره تماس خود را وارد کنید.")
        st.stop()
    
    # صفحه عملیات (تشخیص محصولات)
    st.title("🌟 YOLOv11 شناسایی محصولات")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🎥 شروع شناسایی", key="start_detection"):
            st.session_state.stop_processing = False
    with col2:
        if st.button("⛔ پایان عملیات", key="end_detection"):
            st.session_state.stop_processing = True
            if st.session_state.camera:
                st.session_state.camera.release()
                st.session_state.camera = None

    if not st.session_state.stop_processing:
        process_new_frame()
        if st.session_state.frame is not None:
            st.image(cv2.cvtColor(st.session_state.frame, cv2.COLOR_BGR2RGB), channels="RGB")
        st_autorefresh(interval=100, key="video_refresh")
    else:
        show_final_list()

if __name__ == "__main__":
    streamlit_app()