import cv2
import streamlit as st
from ultralytics import YOLO
from collections import defaultdict
import json

# بارگذاری مدل YOLO
yolo = YOLO('best.pt')

# استفاده از session_state برای ذخیره اطلاعات
if "detected_objects" not in st.session_state:
    st.session_state.detected_objects = {}

if "active_objects" not in st.session_state:
    st.session_state.active_objects = defaultdict(int)

if "stop_processing" not in st.session_state:
    st.session_state.stop_processing = False

if "purchase_submitted" not in st.session_state:
    st.session_state.purchase_submitted = False

# تنظیمات مربوط به زمان ماندگاری اشیاء
FRAME_LIFETIME = 10

# CSS سفارشی برای زیباتر کردن ظاهر برنامه
# CSS سفارشی برای زیباتر کردن ظاهر برنامه و افزایش اندازه متن‌ها
def add_custom_css():
    st.markdown(
        """
        <style>
        body {
            font-family: 'IRANSans', sans-serif;
            background-color: #e8f5e9; /* سفید مایل به سبز */
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'IRANSans', sans-serif;
            font-size: 26px; /* بزرگ‌تر شدن تیترها */
            color: #2e7d32; /* سبز پررنگ‌تر */
        }
        .stTextArea>div>textarea {
            font-size: 18px; /* بزرگ‌تر شدن متن ورودی‌ها */
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            font-size: 20px; /* بزرگ‌تر شدن دکمه‌ها */
            padding: 15px 30px; /* بهبود اندازه دکمه */
            margin: 15px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .reset-button>button, .submit-button>button {
            background-color: #FF5733;
            color: white;
            border-radius: 8px;
            font-size: 20px; /* بزرگ‌تر شدن دکمه‌های مخصوص */
            padding: 15px 30px;
        }
        .reset-button>button:hover, .submit-button>button:hover {
            background-color: #E63939;
        }
        div.stMarkdown > div {
            font-size: 20px; /* بزرگ‌تر شدن متن‌های Markdown */
            line-height: 1.8; /* بهبود فاصله بین خطوط */
        }
        .stDataFrame {
            font-size: 16px; /* بزرگ‌تر شدن جدول‌ها */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# مدیریت پردازش ویدیو
def video_processing():
    detected_objects = st.session_state.detected_objects
    active_objects = st.session_state.active_objects

    # تنظیم دوربین
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        st.error("❌ وب‌کم در دسترس نیست!")
        return

    stframe = st.empty()
    with st.sidebar:  # اضافه کردن لیست اشیاء به نوار سمت راست
        st.write("🛒 **اشیاء شناسایی‌شده (ریل‌تایم):**")
        object_list_placeholder = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("⚠️ عدم دریافت فریم از وب‌کم!")
            break

        # شناسایی اشیاء با YOLO
        results = yolo(frame, imgsz=640)
        current_objects = set()

        for result in results:
            boxes = result.boxes
            names = result.names

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                label = names[int(box.cls)]
                current_objects.add(label)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        for obj in current_objects:
            if obj not in active_objects:
                detected_objects[obj] = detected_objects.get(obj, 0) + 1
            active_objects[obj] = FRAME_LIFETIME

        to_remove = []
        for obj in active_objects:
            if obj not in current_objects:
                active_objects[obj] -= 1
                if active_objects[obj] <= 0:
                    to_remove.append(obj)

        for obj in to_remove:
            del active_objects[obj]

        # به‌روزرسانی لیست در سمت راست
        with object_list_placeholder.container():
            st.markdown("<div style='font-size: 20px;'>", unsafe_allow_html=True)
            for obj, count in detected_objects.items():
                st.write(f"🟢 **{obj}**: {count} بار")
            st.markdown("</div>", unsafe_allow_html=True)

        # نمایش فریم
        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

        # توقف پردازش
        if st.session_state.stop_processing:
            break

    cap.release()
    cv2.destroyAllWindows()

# نمایش لیست تکمیلی با امکان تغییر تعداد
def show_final_list():
    st.subheader("🛠️ لیست نهایی اشیاء شناسایی‌شده:")
    detected_objects = st.session_state.detected_objects

    for obj, count in list(detected_objects.items()):  # استفاده از list برای حذف صفرها
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

    # دکمه ثبت خرید
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("📦 ثبت خرید", key="submit_purchase", help="ثبت لیست خرید نهایی"):
        st.session_state.purchase_submitted = True
        filtered_data = {k: v for k, v in detected_objects.items() if v > 0}  # حذف صفرها
        purchase_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)
        st.text_area("🔗 داده‌های ارسال‌شده (JSON):", purchase_data, height=250)
        st.success("✅ خرید ثبت شد! برنامه متوقف شد.")
        st.stop()  # توقف برنامه

    # دکمه شروع دوباره
    if st.button("🔄 شروع دوباره", key="reset_button", help="شروع یک عملیات جدید"):
        st.session_state.detected_objects = {}
        st.session_state.active_objects = defaultdict(int)
        st.session_state.stop_processing = False

# رابط کاربری
def streamlit_app():
    st.set_page_config(page_title="شناسایی اشیاء", layout="wide")
    add_custom_css()

    st.title("🌟 YOLOv11 شناسایی محصولات با")
    st.write(" .برای شناسایی محصولات از دوربین استفاده می‌کند YOLOv11 این اپلیکیشن با")

    col1, col2 = st.columns([1, 1])

    with col1:
        if not st.session_state.stop_processing:
            if st.button("شروع شناسایی", key="start_button"):
                st.session_state.stop_processing = False
                video_processing()

    with col2:
        if st.session_state.stop_processing:
            st.write("✅ پردازش متوقف شد.")
        else:
            if st.button("پایان عملیات", key="end_button"):
                st.session_state.stop_processing = True

    # نمایش لیست تکمیلی در پایان عملیات
    if st.session_state.stop_processing:
        show_final_list()

# اجرای اپلیکیشن
if __name__ == "__main__":
    streamlit_app()
