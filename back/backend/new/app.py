import os
# Disable Streamlit's watcher to avoid torch.classes errors
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import cv2
import streamlit as st
from ultralytics import YOLO
from collections import defaultdict
import json

# بارگذاری مدل YOLO
yolo = YOLO('best.pt')

# تنظیمات مربوط به زمان ماندگاری اشیاء
FRAME_LIFETIME = 10

# مقداردهی اولیه وضعیت‌های session_state در اولین اجرا
def initialize_session():
    if "detected_objects" not in st.session_state:
        st.session_state.detected_objects = {}
    if "active_objects" not in st.session_state:
        st.session_state.active_objects = defaultdict(int)
    if "stop_processing" not in st.session_state:
        st.session_state.stop_processing = False
    if "purchase_submitted" not in st.session_state:
        st.session_state.purchase_submitted = False
    if "frame" not in st.session_state:
        st.session_state.frame = None
    if "camera" not in st.session_state:
        st.session_state.camera = None

# CSS سفارشی برای زیباتر کردن ظاهر برنامه
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

# پردازش فریم جدید از دوربین
def process_new_frame():
    detected_objects = st.session_state.detected_objects
    active_objects = st.session_state.active_objects

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
    current_objects = set()

    for result in results:
        boxes = result.boxes
        names = result.names

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            label = names[int(box.cls)]
            current_objects.add(label)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    for obj in current_objects:
        if obj not in active_objects:
            detected_objects[obj] = detected_objects.get(obj, 0) + 1
        active_objects[obj] = FRAME_LIFETIME

    to_remove = [obj for obj in active_objects if obj not in current_objects]
    for obj in to_remove:
        active_objects[obj] -= 1
        if active_objects[obj] <= 0:
            del active_objects[obj]

    st.session_state.frame = frame

# نمایش لیست نهایی اشیاء شناسایی‌شده
def show_final_list():
    st.subheader("🛠️ لیست نهایی اشیاء شناسایی‌شده:")
    detected_objects = st.session_state.detected_objects

    for obj, count in list(detected_objects.items()):
        if count == 0:
            del detected_objects[obj]
        else:
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
        purchase_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)
        st.text_area("🔗 داده‌های ارسال‌شده (JSON):", purchase_data, height=250)
        st.success("✅ خرید ثبت شد! برنامه متوقف شد.")
        st.session_state.stop_processing = True
        if st.session_state.camera:
            st.session_state.camera.release()
        st.experimental_rerun()

    if st.button("🔄 شروع دوباره", key="reset_button"):
        st.session_state.detected_objects = {}
        st.session_state.active_objects = defaultdict(int)
        st.session_state.stop_processing = False
        st.session_state.purchase_submitted = False
        if st.session_state.camera:
            st.session_state.camera.release()
        st.session_state.camera = None
        st.experimental_rerun()

# رابط اصلی برنامه
def streamlit_app():
    st.set_page_config(page_title="شناسایی اشیاء", layout="wide")
    initialize_session()
    add_custom_css()

    st.title("🌟 YOLOv11 شناسایی محصولات با")
    st.write(".برای شناسایی محصولات از دوربین استفاده می‌کند YOLOv11 این اپلیکیشن با")

    col1, col2 = st.columns([1, 1])
    with col1:
        if not st.session_state.stop_processing:
            if st.button("🎥 شروع شناسایی"):
                st.session_state.stop_processing = False

    with col2:
        if not st.session_state.stop_processing:
            if st.button("⛔ پایان عملیات"):
                st.session_state.stop_processing = True
        if st.session_state.stop_processing and st.session_state.camera:
            st.session_state.camera.release()
            st.session_state.camera = None

    if not st.session_state.stop_processing:
        process_new_frame()
        stframe = st.empty()
        if st.session_state.frame is not None:
            stframe.image(cv2.cvtColor(st.session_state.frame, cv2.COLOR_BGR2RGB), channels="RGB")
        st.experimental_rerun()
    else:
        show_final_list()

if __name__ == "__main__":
    streamlit_app()
