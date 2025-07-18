import requests
#from sympy.printing.pytorch import torch
import torch
from ultralytics import YOLO
from pathlib import Path
import json
import cv2
import time
import pandas as pd
import streamlit as st




# تابع برای بارگیری فایل مپینگ محصولات
def load_product_mapping():
    try:
        mapping_file = Path(__file__).parent / "product_name_mapping.json"
        if not mapping_file.exists():
            st.error("فایل مپینگ محصولات یافت نشد!")
            return []
        with open(mapping_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"خطا در بارگیری فایل مپینگ: {str(e)}")
        return []





# تابع برای تبدیل نام انگلیسی به فارسی
def get_fa_name(en_label, mapping):
    cleaned_label = en_label.strip().lower().replace(" ", "_").replace("-", "_")
    for item in mapping:
        mapping_label = item["en"].strip().lower().replace(" ", "_").replace("-", "_")
        if mapping_label == cleaned_label:
            return item["fa"]
    return f"نامشخص ({en_label})"







# ----------------- تنظیمات CSS سفارشی -----------------
def add_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary: #0f20db;
        --primary-light: #888ecf;
        --background: #e2e8f0;
        --card-bg: #ffffff;
        --text: #2d3748;
        --text-light: #718096;
        --success: #48bb78;
        --danger: #e53e3e;
        --table-header: #0f20db;
        --table-row-odd: #ffffff;
        --table-row-even: #f8fafc;
        --table-border: #e0e0e0;
        --table-hover: #e6e9ff;
    }

    .stApp {
        font-family: 'YekanBakh', Tahoma, sans-serif !important; 
        background-color: var(--background) !important;
        color: var(--text) !important;
    }
    h1, h2, h3 {
        text-align: center;
        color: var(--text) !important;
        font-weight: 800 !important;
    }
    button {
        background-color: var(--primary) !important;
        color: white !important;
        border-radius: 10px;
        font-size: 18px;
        padding: 12px 24px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(15, 32, 219, 0.2);
    }
    button:hover {
        background-color: var(--primary-light) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(15, 32, 219, 0.3);
    }
    .stButton>button {
        width: 100%;
    }

    /* استایل‌های سفارشی برای تمام جداول */
    .stDataFrame, .dataframe {
        width: 100% !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08) !important;
        margin: 20px 0 !important;
        font-family: 'YekanBakh', Tahoma, sans-serif !important;
        border-collapse: collapse !important;
        animation: fadeIn 0.5s ease !important;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stDataFrame th, .dataframe th {
        background: linear-gradient(135deg, var(--table-header) 0%, #2c3fe0 100%) !important;
        color: white !important;
        padding: 16px 20px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        text-align: center !important;
        text-shadow: 0 1px 1px rgba(0,0,0,0.1) !important;
    }

    .stDataFrame td, .dataframe td {
        padding: 14px 20px !important;
        border-bottom: 1px solid var(--table-border) !important;
        text-align: left !important;
        font-size: 16px !important;
        transition: background 0.3s ease !important;
    }

    .stDataFrame tr, .dataframe tr {
        background-color: var(--table-row-odd) !important;
    }

    .stDataFrame tr:nth-child(even), .dataframe tr:nth-child(even) {
        background-color: var(--table-row-even) !important;
    }

    .stDataFrame tr:hover td, .dataframe tr:hover td {
        background-color: var(--table-hover) !important;
    }

    .stDataFrame .product-name, .dataframe .product-name {
        font-weight: 600 !important;
        color: var(--text) !important;
        text-align: left !important;
        padding-left: 25px !important;
    }

    .stDataFrame .product-count, .dataframe .product-count {
        font-weight: 700 !important;
        color: var(--primary) !important;
        font-size: 18px !important;
        position: relative !important;
        text-align: left !important;
    }

    .stDataFrame .product-count::after, .dataframe .product-count::after {
        content: "عدد" !important;
        font-size: 12px !important;
        color: var(--text-light) !important;
        position: absolute !important;
        left: 5px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
    }

    .empty-cart {
        text-align: center;
        padding: 30px;
        color: var(--text-light);
        font-style: italic;
        font-size: 18px;
        background-color: var(--card-bg);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 20px 0;
    }

    .success-toast {
        background-color: var(--success) !important;
        color: white !important;
        font-family: 'YekanBakh' !important;
        font-size: 16px !important;
        border-radius: 8px !important;
    }

    /* استایل‌های دکمه‌های ویرایش */
    .edit-btn {
        padding: 8px 15px !important;
        font-size: 20px !important;
        min-width: 50px !important;
    }

    .delete-btn {
        background-color: var(--danger) !important;
        color: white !important;
        font-size: 16px !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
    }

    .delete-btn:hover {
        background-color: #c53030 !important;
    }

    .product-display {
        font-size: 18px;
        font-weight: 600;
        padding: 10px 15px;
        background-color: #f8fafc;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .product-name-display {
        flex-grow: 1;
        text-align: left !important;
        padding-left: 15px;
    }

    .product-count-display {
        font-weight: 700;
        color: var(--primary);
        font-size: 20px;
        min-width: 80px;
        text-align: left !important;
    }

    .edit-actions {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    /* انیمیشن برای اضافه شدن محصول */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .pulse-animation {
        animation: pulse 0.5s ease;
    }

    .edit-section {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .editable-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        font-family: 'YekanBakh', Tahoma, sans-serif;
    }

    .editable-table th {
        background: linear-gradient(135deg, var(--table-header) 0%, #2c3fe0 100%);
        color: white;
        padding: 16px 20px;
        font-weight: 700;
        font-size: 18px;
        text-align: center;
    }

    .editable-table td {
        padding: 14px 20px;
        border-bottom: 1px solid var(--table-border);
        text-align: center;
        font-size: 16px;
    }

    .editable-table tr {
        background-color: var(--table-row-odd);
    }

    .editable-table tr:nth-child(even) {
        background-color: var(--table-row-even);
    }

    .editable-table tr:hover td {
        background-color: var(--table-hover);
    }

    .action-cell {
        display: flex;
        justify-content: center;
        gap: 10px;
    }

    .editable-btn {
        min-width: 80px;
        padding: 8px 12px !important;
    }

    /* استایل جدید برای پیام موفقیت ثبت نهایی */
    .success-message-card {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
        color: black !important;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-top: 30px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }

    .success-message-card h3 {
        color: black !important;
        margin-bottom: 15px;
    }

    .success-message-card p {
        font-size: 18px;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ----------------- مقداردهی اولیه session_state -----------------
def init_session_state():
    required_states = {
        "purchase_started": False,
        "running": False,
        "purchase_list": {},
        "tracked_objects": {},
        "model": None,
        "cap": None,
        "final_list": None,
        "camera_initialized": False,
        "last_update": 0,
        "df_placeholder": None,
        "product_mapping": []  # اضافه کردن نگاشت محصولات
    }

    for key, value in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # بارگیری نگاشت نام محصولات
    if not st.session_state.product_mapping:
        st.session_state.product_mapping = load_product_mapping()

        # بررسی دسترسی به GPU
    if torch.cuda.is_available():
        device = "cuda"
        st.sidebar.success("✅ GPU فعال شد! پردازش تصویر روی کارت گرافیک انجام می‌شود.")
    else:
        device = "cpu"
        st.sidebar.warning("⚠️ GPU یافت نشد! پردازش روی CPU انجام می‌شود.")

        # بارگذاری مدل روی دستگاه مناسب
    if st.session_state.model is None:
        st.session_state.model = YOLO('best (1).pt').to(device)

        # تنظیمات بهینه‌سازی برای GPU
    if device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.set_flush_denormal(True)


# ----------------- صفحه اصلی قبل از شروع خرید -----------------
def show_initial_page():
    container = st.container()
    with container:
        st.title("🛒 سیستم خرید هوشمند")
        col_left, col_center, col_right = st.columns([1, 1, 1])

        with col_left:
            # ایجاد فضای بیشتر بالای دکمه
            st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)

            if st.button("شروع عملیات خرید", key="start_btn", use_container_width=True):
                # باز کردن صفحه در یک تب جدید که قابل بسته شدن است
                st.markdown(
                    """
                    <script>
                    window.open('', '_blank');
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                st.session_state.purchase_started = True
                st.session_state.running = True
                st.session_state.purchase_list = {}
                st.session_state.tracked_objects = {}
                st.session_state.model = YOLO('best (1).pt')
                st.session_state.camera_initialized = False
                st.rerun()

            # اضافه کردن آیکون‌ها زیر دکمه با ایموجی‌های ساده
            st.markdown(
                """
                <div style="text-align: center; margin-top: 30px; font-size: 36px;">
                    <div style="margin-bottom: 15px;">📷</div>
                    <div style="margin-bottom: 15px;">🛒</div>
                    <div>🤖</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

        with col_center:
            st.markdown(
                "<div style='text-align:center; padding-top: 60px;'><strong>برای شروع فرآیند خرید از دکمه سمت چپ استفاده کنید</strong></div>",
                unsafe_allow_html=True
            )

            # اضافه کردن فلش با ایموجی
            st.markdown(
                """
                <div style="text-align: center; margin-top: 30px; font-size: 36px;">
                    ⬅️
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_right:
            # بخش راهنمای استفاده با راست‌چین شدن محتوا
            st.markdown("""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h3 style="color: #0f20db; border-bottom: 2px solid #0f20db; padding-bottom: 10px; text-align: right;">راهنمای استفاده</h3>
            <ol style="padding-right: 20px; line-height: 2; direction: rtl; text-align: right;">
                <li>دکمه «شروع عملیات» را فشار دهید</li>
                <li>محصول را مقابل دوربین قرار دهید</li>
                <li>برای چند ثانیه محصول را جلوی دوربین قرار دهید و سپس از کادر خارج کنید</li>
                <li>این کار را برای تمام محصولاتتان انجام دهید</li>
                <li>پس از اتمام خرید، دکمه پایان عملیات را بزنید</li>
                <li>در صفحه نهایی می‌توانید لیست را ویرایش کنید</li>
                <li>با زدن دکمه ثبت نهایی، لیست خرید ارسال می‌شود</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)


# ----------------- فاز دوربین و تشخیص محصولات -----------------
def run_camera():
    # بارگیری نگاشت نام محصولات
    if "product_mapping" not in st.session_state:
        st.session_state.product_mapping = load_product_mapping()

    # مقداردهی اولیه متغیرهای ضروری
    if "purchase_list" not in st.session_state:
        st.session_state.purchase_list = {}

    if "tracked_objects" not in st.session_state:
        st.session_state.tracked_objects = {}

    # ایجاد طرح‌بندی اصلی
    col_left, col_center, col_right = st.columns([1, 2, 1])

    # ناحیه سمت چپ: سبد خرید
    with col_left:
        st.subheader("🛍️ سبد خرید شما")
        st.session_state.df_placeholder = st.empty()

    # ناحیه سمت راست: کنترل‌ها
    with col_right:
        st.subheader("📋 راهنما")
        # راست‌چین کردن متن راهنما
        st.markdown("""
        <div style="background-color: #f8fafc; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h3 style="color: #0f20db; border-bottom: 2px solid #0f20db; padding-bottom: 10px; text-align: center;">دستورالعمل استفاده</h3>
        <ol style="padding-right: 20px; line-height: 2; direction: rtl; text-align: right;">
            <li>محصول را مقابل دوربین قرار دهید</li>
            <li>برای چند ثانیه محصول را جلوی دوربین نگه دارید</li>
            <li>محصول را از کادر خارج کنید تا به سبد اضافه شود</li>
            <li>پس از اتمام، دکمه پایان عملیات را بزنید</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

        # دکمه پایان عملیات
        if st.button("⏹️ پایان عملیات", key="end_camera", type="primary", use_container_width=True,
                     help="پس از اتمام خرید این دکمه را فشار دهید"):
            st.session_state.running = False
            if st.session_state.cap and st.session_state.cap.isOpened():
                st.session_state.cap.release()
            st.rerun()

        # اضافه کردن آیکون‌ها زیر دکمه
        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px; font-size: 36px;">
                <div style="display: inline-block; margin: 0 10px;">🛒</div>
                <div style="display: inline-block; margin: 0 10px; color: #48bb78;">✅</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # راه‌اندازی دوربین
    if not st.session_state.camera_initialized:
        try:
            st.session_state.cap = cv2.VideoCapture(0)
            st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            st.session_state.cap.set(cv2.CAP_PROP_FPS, 30)
            st.session_state.camera_initialized = True
        except Exception as e:
            st.error(f"خطا در راه‌اندازی دوربین: {str(e)}")
            st.session_state.running = False
            st.rerun()
            return

    # ناحیه مرکزی: نمایش دوربین
    video_placeholder = col_center.empty()
    DETECTION_TIMEOUT = 0.5  # زمان عدم مشاهده برای ثبت محصول (ثانیه)
    MIN_DETECTION_TIME = 1  # حداقل زمان حضور در تصویر برای ثبت محصول (ثانیه)
    last_update_time = time.time()
    # تعیین دستگاه پردازشی
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        while st.session_state.running:
            if not st.session_state.cap or not st.session_state.cap.isOpened():
                st.error("اتصال به دوربین از دست رفته است")
                st.session_state.running = False
                break

            ret, frame = st.session_state.cap.read()
            if not ret:
                st.error("خطا در دریافت تصویر از دوربین")
                time.sleep(0.1)
                continue

            # کاهش اندازه تصویر برای افزایش سرعت پردازش
            resized_frame = cv2.resize(frame, (320, 240))

            # انجام تشخیص با استفاده از GPU
            results = st.session_state.model.track(
                resized_frame,
                persist=True,
                imgsz=320,
                conf=0.6,
                verbose=False,
                device=device,  # استفاده از دستگاه تعیین شده
                half=True if device == "cuda" else False  # استفاده از دقت نیمه-صحیح برای GPU
            )

            # شناسایی اشیاء - تمام اشیاء در فریم
            current_frame_detections = set()
            current_time = time.time()

            for result in results:
                # اگر هیچ تشخیصی وجود نداشت، ادامه بده
                if result.boxes is None or len(result.boxes) == 0:
                    continue

                # استخراج اطلاعات جعبه‌ها و شناسه‌ها
                boxes = result.boxes.xyxy.cpu().numpy()
                clss = result.boxes.cls.cpu().numpy()
                track_ids = result.boxes.id.cpu().numpy() if result.boxes.id is not None else [None] * len(boxes)

                for i in range(len(boxes)):
                    box = boxes[i]
                    cls_idx = int(clss[i].item())
                    en_label = result.names[cls_idx]  # نام انگلیسی محصول
                    track_id = track_ids[i] if track_ids is not None else None

                    if track_id is not None:
                        track_id = int(track_id.item())
                        current_frame_detections.add((en_label, track_id))

                        # ایجاد/به‌روزرسانی رکورد ردیابی
                        if track_id not in st.session_state.tracked_objects:
                            st.session_state.tracked_objects[track_id] = {
                                "en_label": en_label,
                                "first_seen": current_time,
                                "last_seen": current_time,
                                "detected": False
                            }
                        else:
                            # به‌روزرسانی زمان آخرین مشاهده
                            st.session_state.tracked_objects[track_id]["last_seen"] = current_time

                    # رسم کادر و برچسب
                    x1, y1, x2, y2 = map(int, box[:4])
                    scale_x = frame.shape[1] / resized_frame.shape[1]
                    scale_y = frame.shape[0] / resized_frame.shape[0]
                    x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)

                    # رسم مستطیل دور شیء
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 0), 3)

                    # نمایش برچسب و شناسه ردیابی
                    label = f"{en_label} #{track_id}" if track_id is not None else en_label
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 220), 2)

            # بررسی محصولات خارج شده از کادر
            for track_id, obj_info in list(st.session_state.tracked_objects.items()):
                en_label = obj_info["en_label"]

                # اگر شیء در فریم فعلی دیده نشده
                if not any(label == en_label and tid == track_id for label, tid in current_frame_detections):
                    time_since_last_seen = current_time - obj_info["last_seen"]
                    time_present = current_time - obj_info["first_seen"]

                    # شرایط ثبت محصول:
                    # 1. حداقل زمان حضور در تصویر گذشته باشد
                    # 2. زمان کافی از آخرین مشاهده گذشته باشد
                    # 3. قبلاً ثبت نشده باشد
                    if (time_present > MIN_DETECTION_TIME and
                            time_since_last_seen > DETECTION_TIMEOUT and
                            not obj_info["detected"]):

                        # تبدیل نام انگلیسی به فارسی
                        fa_label = get_fa_name(en_label, st.session_state.product_mapping)

                        # افزودن به لیست خرید
                        if fa_label not in st.session_state.purchase_list:
                            st.session_state.purchase_list[fa_label] = 0
                        st.session_state.purchase_list[fa_label] += 1

                        st.session_state.last_update = current_time
                        st.toast(f"✅ محصول {fa_label} به سبد خرید اضافه شد!", icon="🛒")

                        # علامت گذاری به عنوان شناسایی شده
                        st.session_state.tracked_objects[track_id]["detected"] = True

            # حذف اشیاء قدیمی (پس از 10 ثانیه عدم مشاهده)
            for track_id in list(st.session_state.tracked_objects.keys()):
                if current_time - st.session_state.tracked_objects[track_id]["last_seen"] > 10:
                    del st.session_state.tracked_objects[track_id]

            # نمایش ویدئو
            video_placeholder.image(frame, channels="BGR", use_container_width=True)

            # به‌روزرسانی سبد خرید (هر 0.5 ثانیه)
            if current_time - last_update_time > 0.5:
                last_update_time = current_time

                # نمایش جدول سبد خرید (تغییر اصلی در این بخش)
                if st.session_state.purchase_list:
                    # ساخت DataFrame برای نمایش داده‌ها (بدون ستون ردیف)
                    df = pd.DataFrame(
                        {
                            "نام محصول": list(st.session_state.purchase_list.keys()),
                            "تعداد": list(st.session_state.purchase_list.values()),
                        }
                    )
                    
                    # نمایش جدول با استایل‌های سفارشی
                    st.session_state.df_placeholder.dataframe(
                        df,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "نام محصول": st.column_config.TextColumn(
                                width="medium",
                                help="نام محصول تشخیص داده شده"
                            ),
                            "تعداد": st.column_config.NumberColumn(
                                "تعداد",
                                format="%d عدد",
                                help="تعداد محصولات تشخیص داده شده"
                            )
                        }
                    )
                else:
                    st.session_state.df_placeholder.markdown(
                        '<div class="empty-cart">سبد خرید شما خالی است<br>محصولات را مقابل دوربین قرار دهید</div>',
                        unsafe_allow_html=True
                    )

            time.sleep(0.03)  # کاهش مصرف CPU

    except Exception as e:
        st.error(f"خطا در پردازش تصویر: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
    finally:
        # آزادسازی منابع دوربین
        if st.session_state.cap and st.session_state.cap.isOpened():
            st.session_state.cap.release()
        st.session_state.cap = None
        st.session_state.camera_initialized = False


# ----------------- صفحه نهایی جهت ویرایش سبد خرید -----------------
def show_final_page():
    st.title("✅ تکمیل فرآیند خرید")
    st.markdown("---")

    # نمایش لیست قابل ویرایش
    st.subheader("📋 لیست خرید نهایی")

    if not st.session_state.purchase_list:
        st.info("هیچ محصولی در سبد خرید وجود ندارد")
    else:
        # ساخت DataFrame برای نمایش داده‌ها
        df = pd.DataFrame(
            {
                "ردیف": range(1, len(st.session_state.purchase_list) + 1),
                "نام محصول": list(st.session_state.purchase_list.keys()),
                "تعداد": list(st.session_state.purchase_list.values()),
            }
        )

        # نمایش جدول با استایل‌های سفارشی (چپ چین)
        st.markdown("""
        <style>
            div[data-testid="stDataFrame"] table {
                width: 100% !important;
            }
            div[data-testid="stDataFrame"] th, 
            div[data-testid="stDataFrame"] td {
                text-align: left !important;
            }
        </style>
        """, unsafe_allow_html=True)

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "ردیف": st.column_config.NumberColumn(width="small"),
                "نام محصول": st.column_config.TextColumn(width="medium"),
                "تعداد": st.column_config.NumberColumn(width="small"),
            }
        )

        # ویرایش دستی مقادیر
        st.subheader("✏️ ویرایش محصولات")

        # ایجاد رابط کاربری برای ویرایش با استفاده از کامپوننت‌های Streamlit
        for product, count in list(st.session_state.purchase_list.items()):
            with st.container():
                st.markdown(f'<div class="product-display product-edit-container">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([4, 2, 4])

                with col1:
                    st.markdown(f"<div class='product-name-display'>{product}</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown(f"<div class='product-count-display'>{count} عدد</div>", unsafe_allow_html=True)

                with col3:
                    col_dec, col_inc, col_del = st.columns(3)

                    with col_dec:
                        if st.button("➖ کاهش", key=f"dec_{product}", use_container_width=True):
                            st.session_state.purchase_list[product] -= 1
                            if st.session_state.purchase_list[product] <= 0:
                                del st.session_state.purchase_list[product]
                            st.rerun()

                    with col_inc:
                        if st.button("➕ افزایش", key=f"inc_{product}", use_container_width=True):
                            st.session_state.purchase_list[product] += 1
                            st.rerun()

                    with col_del:
                        if st.button("❌ حذف", key=f"del_{product}", type="secondary", use_container_width=True):
                            del st.session_state.purchase_list[product]
                            st.rerun()

                st.markdown(f'</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 شروع دوباره عملیات خرید", type="primary", use_container_width=True,
                     help="شروع فرآیند خرید از ابتدا"):
            st.session_state.purchase_started = False
            st.session_state.running = False
            st.session_state.purchase_list = {}
            st.session_state.tracked_objects = {}
            st.session_state.final_list = None
            st.rerun()

    with col2:
        if st.button("✅ ثبت نهایی خرید", type="primary", use_container_width=True,
                     help="ثبت نهایی لیست خرید و ارسال آن"):
            st.session_state.final_list = dict(st.session_state.purchase_list)

            try:
                # ارسال داده به Flask
                response = requests.post(
                    "http://localhost:5001/submit",
                    json=st.session_state.final_list,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    # نمایش پیام موفقیت
                    st.success("✅ لیست خرید با موفقیت ثبت شد!")


                    # نمایش پیام نهایی و بستن تب
                    st.markdown(
                        """
                        <div class="success-message-card">
                            <h3>خرید شما با موفقیت ثبت شد!</h3>
                            <p>صفحه در حال بسته شدن است ...</p>
                        </div>
                        <script>
                        setTimeout(function() {
                            window.close();
                        }, 3000);
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error(f"خطا در ثبت خرید! کد خطا: {response.status_code}")
                    st.json(response.json())

            except Exception as e:
                st.error(f"خطا در ارتباط با سرور: {str(e)}")


# ----------------- تابع اصلی -----------------
def main():
    st.set_page_config(
        page_title="سیستم خرید هوشمند",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    add_custom_css()
    init_session_state()

    if not st.session_state.purchase_started:
        show_initial_page()
    else:
        if st.session_state.running:
            run_camera()
        else:
            show_final_page()


if __name__ == "__main__":
    main()