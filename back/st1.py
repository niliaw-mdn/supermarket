import cv2
import streamlit as st
from ultralytics import YOLO
from collections import defaultdict
import json

# Set the page config as the first Streamlit command
st.set_page_config(page_title="شناسایی اشیاء", layout="wide")

# Custom CSS for styling
def add_custom_css():
    st.markdown(
        """
        <style>
        .appview-container .main {
            background-color: #e2e8f0 !important;
            font-family: 'IRANSans', sans-serif;
        }

        .st-emotion-cache-z5fcl4 {
            padding: 2rem;
        }

           .stHorizontalBlock.st-emotion-cache-ocqkz7.eiemyj0 {
           margin-top: 30px
            display: flex;
            justify-content: center;  /* Horizontally center the content */
            align-items: center;      /* Vertically center the content */
            height: 100%;             /* Take full height of the container */
        }

        /* Center buttons specifically */
        .stHorizontalBlock.st-emotion-cache-ocqkz7.eiemyj0 button {
            margin: 0 auto;  /* Automatically adjusts the margin to center the buttons */
            display: block;  /* Make the button block level to respect margin auto */
        }

        
        /* Header section */
        .stAppHeader {
            background-color: #636bbf !important;
            color: white !important;
        }

        /* The 'Deploy' button and related actions */
        .stAppDeployButton button {
            background-color: transparent !important;
            color: white !important;
        }

        .stAppDeployButton button:hover {
             background-color: transparent !important;
             transform: scale(1.1); /* Increase the size of the text */
            font-size: 20px;
        }

        

        /* Menu button */
        .stMainMenu button {
            background-color: transparent !important;
            color: white !important;
        }

        


        /* Headings */
        h1, h2, h3 {
            color: gray !important;
            text-align: center;
        }

        /* Buttons */
        button {
            background-color: #0f20db !important;
            color: white !important;
            border-radius: 8px !important;
            font-size: 18px !important;
            padding: 10px 20px !important;
        }

        button:hover {
            background-color: #888ecf !important;
            border:none;
0        }

        /* Text area */
        textarea {
            font-size: 16px !important;
        }

        /* Markdown text */
        .stMarkdown {
            font-size: 18px !important;
            line-height: 1.8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def set_background_color():
    st.markdown(
        """
        <style>
        /* Set background color for the whole page */
        .stApp {
            background-color: #e2e8f0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_background_color()
add_custom_css()  


# YOLO model initialization
yolo = YOLO('best.pt')

# Session state initialization
if "detected_objects" not in st.session_state:
    st.session_state.detected_objects = {}
if "active_objects" not in st.session_state:
    st.session_state.active_objects = defaultdict(int)
if "stop_processing" not in st.session_state:
    st.session_state.stop_processing = False
if "purchase_submitted" not in st.session_state:
    st.session_state.purchase_submitted = False

# Settings for object lifetime
FRAME_LIFETIME = 10

# Function for video processing and object detection
def video_processing():
    detected_objects = st.session_state.detected_objects
    active_objects = st.session_state.active_objects

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    if not cap.isOpened():
        st.error("❌ وب‌کم در دسترس نیست!")
        return

    stframe = st.empty()
    with st.sidebar:
        st.write("🛒 **اشیاء شناسایی‌شده (ریل‌تایم):**")
        object_list_placeholder = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("⚠️ عدم دریافت فریم از وب‌کم!")
            break

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

        with object_list_placeholder.container():
            st.markdown("<div style='font-size: 20px;'>", unsafe_allow_html=True)
            for obj, count in detected_objects.items():
                st.write(f"🟢 **{obj}**: {count} بار")
            st.markdown("</div>", unsafe_allow_html=True)

        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

        if st.session_state.stop_processing:
            break

    cap.release()
    cv2.destroyAllWindows()

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

    if st.button("📦 ثبت خرید", key="submit_purchase", help="ثبت لیست خرید نهایی"):
       st.session_state.purchase_submitted = True
       filtered_data = {k: v for k, v in detected_objects.items() if v > 0}
       purchase_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)
       st.text_area("🔗 داده‌های ارسال‌شده (JSON):", purchase_data, height=250)
       st.success("✅ خرید ثبت شد! برنامه متوقف شد.")
       st.stop()


    if st.session_state.purchase_submitted:
        st.markdown("### 🧾 فاکتور خرید نهایی")
        filtered_data = {k: v for k, v in detected_objects.items() if v > 0}

        if filtered_data:
            invoice_rows = [{"نام محصول": k, "تعداد": v} for k, v in filtered_data.items()]
            st.table(invoice_rows)
            st.success("✅ خرید ثبت شد!")
        else:
            st.warning("هیچ محصولی برای نمایش وجود ندارد.")

    if st.button("🔄 شروع دوباره", key="reset_button", help="شروع یک عملیات جدید"):
        st.session_state.detected_objects = {}
        st.session_state.active_objects = defaultdict(int)
        st.session_state.stop_processing = False
        st.session_state.purchase_submitted = False


def show_invoice_modal():
    st.markdown("### 🧾 فاکتور خرید نهایی")
    st.markdown('<div style="background-color: white; padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
    detected_objects = st.session_state.detected_objects
    filtered_data = {k: v for k, v in detected_objects.items() if v > 0}

    if not filtered_data:
        st.warning("هیچ کالایی ثبت نشده است.")
    else:
        st.table([{"نام کالا": k, "تعداد": v} for k, v in filtered_data.items()])
        st.success("✅ خرید شما با موفقیت ثبت شد!")

    if st.button("🔄 شروع دوباره", key="reset_button"):
        st.session_state.purchase_submitted = False
        st.session_state.detected_objects = {}
        st.session_state.active_objects = defaultdict(int)
        st.session_state.stop_processing = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def streamlit_app():
    if st.session_state.purchase_submitted:
        show_invoice_modal()
        return

    st.title("سیستم هوشمند شناسایی محصولات🛒")
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

    if st.session_state.stop_processing:
        show_final_list()


if __name__ == "__main__":
    streamlit_app()
