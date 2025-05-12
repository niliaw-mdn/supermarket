import os
import sys
import threading
import json
import cv2
import streamlit as st
from ultralytics import YOLO
from imutils.video import VideoStream
from collections import defaultdict
from flask import Flask, request, jsonify

# —————— تنظیمات کلی ——————
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
FRONTEND_URL = "http://localhost:3000/api/receive"  # ← این را تغییر بده
FLASK_PORT   = 8888
FRAME_LIFETIME = 10

# —————— اپلیکیشن Flask برای ارائه JSON ——————
flask_app = Flask(__name__)
products_list = {}  # دیکشنری‌ای که محصولات نهایی اینجا نگه داشته می‌شوند

@flask_app.route("/results", methods=["GET"])
def get_results():
    return jsonify(products_list)

def start_flask():
    # اجرا در ترد جدا (daemon=True تا با خاتمهٔ main thread بمیرد)
    flask_app.run(port=FLASK_PORT, debug=False, use_reloader=False)

# —————— Streamlit: حالت GPU برای YOLO ——————
# مطمئن شو که cuda در دسترس است
if not (st.runtime.exists() and hasattr(st.runtime, "cuda") and st.runtime.cuda.is_available()):
    # اگر استریم‌لیت cuda رو نشناخت، می‌تونیم مستقیم torch رو چک کنیم
    import torch
    if not torch.cuda.is_available():
        st.error("کارت گرافیک CUDA در دسترس نیست. برنامه روی GPU اجرا نمی‌شود.")
        st.stop()

# مدل YOLO را روی GPU بارگذاری کن (cuda:0)
yolo = YOLO("best.pt")
yolo.to("cuda:0")
yolo.model.half()
# —————— session init ——————
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
    # ← اطمینان از None بودن vs
    if "vs" not in st.session_state:
        st.session_state.vs = None
# —————— CSS سفارشی ——————
def add_custom_css():
    st.markdown("""
    <style>
      body { font-family: 'IRANSans', sans-serif; background-color: #e8f5e9; }
      h1,h2,h3,h4 { font-family: 'IRANSans', sans-serif; color: #2e7d32; }
      .stButton>button { border-radius:8px; font-size:20px; padding:12px 24px; }
      .submit-button>button { background-color:#FF5733;color:white; }
      .submit-button>button:hover { background-color:#E63939; }
    </style>
    """, unsafe_allow_html=True)

# —————— خواندن ویدئو در ترد جدا ——————
def init_video_stream():
    vs = VideoStream(src=0).start()
    st.session_state.vs = vs

# —————— پردازش فریم جدید ——————
def process_new_frame():
    # ۱) اگر VideoStream مقداردهی نشده، آن‌را مقداردهی کن
    if st.session_state.vs is None:
        st.session_state.vs = VideoStream(src=0).start()

    vs = st.session_state.vs
    frame = vs.read()  # حالا vs حتماً یک VideoStream معتبر است

    if frame is None:
        st.warning("⚠️ عدم دریافت فریم از وب‌کم!")
        st.session_state.stop_processing = True
        return




    # inference با نیم‌دقت و استریم
    results = yolo(frame, device=0, half=True, stream=True, stream_buffer=False)

    current_objects = set()
    for res in results:
        for box in res.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            label = res.names[int(box.cls)]
            current_objects.add(label)
            # رسم‌بند جعبه و برچسب
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)
            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    # به‌روز‌رسانی شمارش و مدت ماندگاری
    det = st.session_state.detected_objects
    active = st.session_state.active_objects
    for obj in current_objects:
        if obj not in active:
            det[obj] = det.get(obj, 0) + 1
        active[obj] = FRAME_LIFETIME

    # کاهش عمر اشیاء غایب
    for obj in list(active):
        if obj not in current_objects:
            active[obj] -= 1
            if active[obj] <= 0:
                del active[obj]

    st.session_state.frame = frame

# —————— نمایش نهایی و ارسال JSON ——————
def show_final_list_and_submit():
    st.subheader("🛠️ لیست نهایی اشیاء شناسایی‌شده:")
    det = st.session_state.detected_objects

    # کنترل افزایش/کاهش تعداد
    for obj, count in list(det.items()):
        cols = st.columns([1,1,5])
        with cols[0]:
            if st.button("➕", key=f"inc_{obj}"): det[obj] += 1
        with cols[1]:
            if st.button("➖", key=f"dec_{obj}"): det[obj] = max(0, det[obj]-1)
        with cols[2]:
            st.write(f"**{obj}**: {det[obj]}")

    st.markdown("---")

    if st.button("📦 ثبت خرید", key="submit_purchase", help="ارسال به فرانت و بستن برنامه"):
        # آماده‌سازی JSON
        filtered = {k:v for k,v in det.items() if v>0}
        # به دیکشنری مشترک Flask بریز
        global products_list
        products_list.clear()
        products_list.update(filtered)

        # ارسال HTTP توسط جاوااسکریپت
        json_str = json.dumps(filtered, ensure_ascii=False)
        js = f"""
        <script>
          // ۱) ارسال JSON به فرانت
          fetch("{FRONTEND_URL}", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({json_str})
          }}).finally(() => {{
            // ۲) بستن پنجره
            window.open('','_self');
            window.close();
          }});
        </script>
        """
        st.components.v1.html(js, height=0)
        # توقف در سمت سرور
        st.session_state.stop_processing = True
        if st.session_state.vs:
            st.session_state.vs.stop()
        st.stop()

# —————— رابط اصلی ——————
def streamlit_app():
    st.set_page_config(page_title="شناسایی اشیاء (GPU)", layout="wide")
    initialize_session()
    add_custom_css()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎥 شروع شناسایی"):
            st.session_state.stop_processing = False
            # ← این خط لازم نیست چون process_new_frame خودش init می‌کند
            # st.session_state.vs = None  
    with col2:
        if st.button("⛔ پایان عملیات"):
            st.session_state.stop_processing = True
            if st.session_state.vs:
                st.session_state.vs.stop()
                st.session_state.vs = None

    if not st.session_state.stop_processing:
        process_new_frame()
        if st.session_state.frame is not None:
            st.image(
                cv2.cvtColor(st.session_state.frame, cv2.COLOR_BGR2RGB),
                channels="RGB",
                use_column_width=True,
            )
        st.experimental_rerun()
    else:
        show_final_list_and_submit()


if __name__ == "__main__":
    streamlit_app()
