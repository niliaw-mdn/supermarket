import os
import signal
import requests
import torch
from ultralytics import YOLO
from pathlib import Path
import json
import cv2
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import random
import math

import html






def to_persian_num(n):
    english_to_persian = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    return ''.join(english_to_persian.get(digit, digit) for digit in str(n))


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


def get_fa_name(en_label, mapping):
    cleaned_label = en_label.strip().lower().replace(" ", "_").replace("-", "_")
    for item in mapping:
        mapping_label = item["en"].strip().lower().replace(" ", "_").replace("-", "_")
        if mapping_label == cleaned_label:
            return item["fa"]
    return f"نامشخص ({en_label})"


def add_custom_css():
    st.markdown("""
    <style>
    /* حذف کامل نوار بالای صفحه */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* تنظیم مجدد فضای صفحه */
    .stApp {
        margin-top: 0;
        padding-top: 60px; /* فضای اضافی برای نوار موجی بالایی */
        padding-bottom: 60px; /* فضای اضافی برای نوار موجی پایینی */
    }
    
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
    
    /* ================= نوار موجی پویا در پایین صفحه ================= */
    .wave-bottom-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 60px;  /* کاهش ارتفاع */
        z-index: -1;
        overflow: hidden;
    }
    
    .wave-bottom {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 200%;
        height: 100%;
        background: linear-gradient(to right, #0f20db, #00a8ff, #0f20db);
        opacity: 0.7;
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        animation: wave-animation 15s linear infinite;
    }
    
    .wave-bottom:nth-child(2) {
        background: linear-gradient(to right, #00a8ff, #0f20db, #00a8ff);
        opacity: 0.5;
        animation: wave-animation 10s linear infinite reverse;
        height: 90%;
    }
    
    .wave-bottom:nth-child(3) {
        background: linear-gradient(to right, #0f20db, #00a8ff, #0f20db);
        opacity: 0.3;
        animation: wave-animation 12s linear infinite;
        height: 80%;
    }
    
    /* ================= نوار موجی پویا در بالای صفحه ================= */
    .wave-top-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        z-index: 9999;
        overflow: hidden;
        transform: rotate(180deg); /* چرخش برای ایجاد اثر موج در بالا */
    }
    
    .wave-top {
        position: absolute;
        top: 0;
        left: 0;
        width: 200%;
        height: 100%;
        background: linear-gradient(to right, #0f20db, #00a8ff, #0f20db);
        opacity: 0.7;
        border-radius: 50% 50% 0 0 / 100% 100% 0 0;
        animation: wave-animation 15s linear infinite;
    }
    
    .wave-top:nth-child(2) {
        background: linear-gradient(to right, #00a8ff, #0f20db, #00a8ff);
        opacity: 0.5;
        animation: wave-animation 10s linear infinite reverse;
        height: 90%;
    }
    
    .wave-top:nth-child(3) {
        background: linear-gradient(to right, #0f20db, #00a8ff, #0f20db);
        opacity: 0.3;
        animation: wave-animation 12s linear infinite;
        height: 80%;
    }
    
    /* انیمیشن مشترک برای نوارهای موجی */
    @keyframes wave-animation {
        0% {
            transform: translateX(0) translateY(0) scaleY(1);
        }
        25% {
            transform: translateX(-25%) translateY(5px) scaleY(1.1); /* تغییرات کوچکتر */
        }
        50% {
            transform: translateX(-50%) translateY(0) scaleY(1);
        }
        75% {
            transform: translateX(-25%) translateY(-5px) scaleY(0.9); /* تغییرات کوچکتر */
        }
        100% {
            transform: translateX(0) translateY(0) scaleY(1);
        }
    }
    
    /* استایل جدید برای جدول پویا */
    .dynamic-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        font-family: 'YekanBakh', Tahoma, sans-serif;
        margin: 20px 0;
        animation: fadeIn 0.5s ease;
        border: 1px solid var(--table-border);
    }
    
    .dynamic-table th {
        background: linear-gradient(135deg, var(--table-header) 0%, #2c3fe0 100%);
        color: white;
        padding: 16px 20px;
        font-weight: 700;
        font-size: 18px;
        text-align: center;
        border: 1px solid var(--table-border);
    }
    
    .dynamic-table td {
        padding: 14px 20px;
        border: 1px solid var(--table-border);
        text-align: center;
        font-size: 16px;
        vertical-align: middle;
    }
    
    .dynamic-table tr {
        background-color: var(--table-row-odd);
        transition: all 0.3s ease;
    }
    
    .dynamic-table tr:nth-child(even) {
        background-color: var(--table-row-even);
    }
    
    .dynamic-table tr:hover {
        background-color: var(--table-hover);
    }
    
    .row-index {
        font-weight: bold;
        color: var(--text);
    }
    
    .product-name {
        font-weight: 600;
        color: var(--text);
    }
    
    .product-count {
        font-weight: 700;
        color: var(--primary);
        font-size: 18px;
    }
    
    .action-buttons {
        display: flex;
        justify-content: center;
        gap: 8px;
    }
    
    .action-btn {
        padding: 6px 10px !important;
        min-width: 35px;
        border-radius: 6px;
        font-size: 14px;
        transition: all 0.2s ease;
        border: 1px solid #e0e0e0 !important;
        background-color: #f8fafc !important;
    }
    
    .action-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .decrease-btn {
        color: #e53e3e !important;
    }
    
    .increase-btn {
        color: #48bb78 !important;
    }
    
    .delete-btn {
        color: #e53e3e !important;
    }
    </style>
    """, unsafe_allow_html=True)


def generate_wave_bottom():
    st.markdown(
        """
        <div class="wave-bottom-container">
            <div class="wave-bottom"></div>
            <div class="wave-bottom"></div>
            <div class="wave-bottom"></div>
        </div>
        """,
        unsafe_allow_html=True
    )


def generate_wave_top():
    st.markdown(
        """
        <div class="wave-top-container">
            <div class="wave-top"></div>
            <div class="wave-top"></div>
            <div class="wave-top"></div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
        "product_mapping": [],  
        "editing": {},  
        "edit_form": None  
    }

    for key, value in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


    if not st.session_state.product_mapping:
        st.session_state.product_mapping = load_product_mapping()


    if torch.cuda.is_available():
        device = "cuda"
        st.sidebar.success("✅ GPU فعال شد! پردازش تصویر روی کارت گرافیک انجام می‌شود.")
    else:
        device = "cpu"
        st.sidebar.warning("⚠️ GPU یافت نشد! پردازش روی CPU انجام می‌شود.")


    if st.session_state.model is None:
        st.session_state.model = YOLO('best (1).pt').to(device)


    if device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.set_flush_denormal(True)


def show_initial_page():
    container = st.container()
    with container:
        st.title("🛒 سیستم خرید هوشمند")
        col_left, col_center, col_right = st.columns([1, 1, 1])

        with col_left:

            st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)

            if st.button("شروع عملیات خرید", key="start_btn", use_container_width=True):

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
                f"<div style='text-align:center; padding-top: 60px;'><strong>برای شروع فرآیند خرید از دکمه سمت چپ استفاده کنید</strong></div>",
                unsafe_allow_html=True
            )


            st.markdown(
                """
                <div style="text-align: center; margin-top: 30px; font-size: 36px;">
                    ⬅️
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_right:

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


def run_camera():

    if "product_mapping" not in st.session_state:
        st.session_state.product_mapping = load_product_mapping()


    if "purchase_list" not in st.session_state:
        st.session_state.purchase_list = {}

    if "tracked_objects" not in st.session_state:
        st.session_state.tracked_objects = {}


    col_left, col_center, col_right = st.columns([1, 2, 1])


    with col_left:
        st.subheader("🛍️ سبد خرید شما")
        st.session_state.df_placeholder = st.empty()


    with col_right:
        st.subheader("📋 راهنما")

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


        if st.button("⏹️ پایان عملیات", key="end_camera", type="primary", use_container_width=True,
                     help="پس از اتمام خرید این دکمه را فشار دهید"):
            st.session_state.running = False
            if st.session_state.cap and st.session_state.cap.isOpened():
                st.session_state.cap.release()
            st.rerun()


        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px; font-size: 36px;">
                <div style="display: inline-block; margin: 0 10px;">🛒</div>
                <div style="display: inline-block; margin: 0 10px; color: #48bb78;">✅</div>
            </div>
            """,
            unsafe_allow_html=True
        )


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


    video_placeholder = col_center.empty()
    DETECTION_TIMEOUT = 0.5  
    MIN_DETECTION_TIME = 1  
    last_update_time = time.time()

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


            resized_frame = cv2.resize(frame, (320, 240))


            results = st.session_state.model.track(
                resized_frame,
                persist=True,
                imgsz=320,
                conf=0.6,
                verbose=False,
                device=device,  
                half=True if device == "cuda" else False  
            )


            current_frame_detections = set()
            current_time = time.time()

            for result in results:

                if result.boxes is None or len(result.boxes) == 0:
                    continue


                boxes = result.boxes.xyxy.cpu().numpy()
                clss = result.boxes.cls.cpu().numpy()
                track_ids = result.boxes.id.cpu().numpy() if result.boxes.id is not None else [None] * len(boxes)

                for i in range(len(boxes)):
                    box = boxes[i]
                    cls_idx = int(clss[i].item())
                    en_label = result.names[cls_idx]  
                    track_id = track_ids[i] if track_ids is not None else None

                    if track_id is not None:
                        track_id = int(track_id.item())
                        current_frame_detections.add((en_label, track_id))


                        if track_id not in st.session_state.tracked_objects:
                            st.session_state.tracked_objects[track_id] = {
                                "en_label": en_label,
                                "first_seen": current_time,
                                "last_seen": current_time,
                                "detected": False
                            }
                        else:

                            st.session_state.tracked_objects[track_id]["last_seen"] = current_time


                    x1, y1, x2, y2 = map(int, box[:4])
                    scale_x = frame.shape[1] / resized_frame.shape[1]
                    scale_y = frame.shape[0] / resized_frame.shape[0]
                    x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)


                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 0), 3)


                    label = f"{en_label} #{track_id}" if track_id is not None else en_label
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 220), 2)


            for track_id, obj_info in list(st.session_state.tracked_objects.items()):
                en_label = obj_info["en_label"]


                if not any(label == en_label and tid == track_id for label, tid in current_frame_detections):
                    time_since_last_seen = current_time - obj_info["last_seen"]
                    time_present = current_time - obj_info["first_seen"]

                    
                    
                    if (time_present > MIN_DETECTION_TIME and
                            time_since_last_seen > DETECTION_TIMEOUT and
                            not obj_info["detected"]):


                        fa_label = get_fa_name(en_label, st.session_state.product_mapping)


                        if fa_label not in st.session_state.purchase_list:
                            st.session_state.purchase_list[fa_label] = 0
                        st.session_state.purchase_list[fa_label] += 1

                        st.session_state.last_update = current_time
                        st.toast(f"✅ محصول {fa_label} به سبد خرید اضافه شد!", icon="🛒")


                        st.session_state.tracked_objects[track_id]["detected"] = True


            for track_id in list(st.session_state.tracked_objects.keys()):
                if current_time - st.session_state.tracked_objects[track_id]["last_seen"] > 10:
                    del st.session_state.tracked_objects[track_id]


            video_placeholder.image(frame, channels="BGR", use_container_width=True)


            if current_time - last_update_time > 0.5:
                last_update_time = current_time


                if st.session_state.purchase_list:


                    df = pd.DataFrame(
                        {
                            "نام محصول": list(st.session_state.purchase_list.keys()),
                            "تعداد": [to_persian_num(count) for count in st.session_state.purchase_list.values()],
                        }
                    )
                    

                    st.session_state.df_placeholder.dataframe(
                        df,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "نام محصول": st.column_config.TextColumn(
                                width="medium",
                                help="نام محصول تشخیص داده شده"
                            ),
                            "تعداد": st.column_config.TextColumn(
                                "تعداد",
                                help="تعداد محصولات تشخیص داده شده"
                            )
                        }
                    )
                else:
                    st.session_state.df_placeholder.markdown(
                        '<div class="empty-cart">سبد خرید شما خالی است<br>محصولات را مقابل دوربین قرار دهید</div>',
                        unsafe_allow_html=True
                    )

            time.sleep(0.03)  

    except Exception as e:
        st.error(f"خطا در پردازش تصویر: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
    finally:

        if st.session_state.cap and st.session_state.cap.isOpened():
            st.session_state.cap.release()
        st.session_state.cap = None
        st.session_state.camera_initialized = False


def modify_quantity(product: str, delta: int):
    """تعداد محصول را تغییر می‌دهد یا در صورت صفر شدن حذف می‌کند."""
    count = st.session_state.purchase_list.get(product, 0)
    new_count = count + delta
    if new_count > 0:
        st.session_state.purchase_list[product] = new_count
    else:
        st.session_state.purchase_list.pop(product, None)


def delete_product(product: str):
    """محصول را از لیست حذف می‌کند."""
    st.session_state.purchase_list.pop(product, None)


def show_final_page():
    st.title("✅ تکمیل فرآیند خرید")
    st.markdown("---")

    st.subheader("📋 لیست خرید نهایی")
    if not st.session_state.purchase_list:
        st.info("هیچ محصولی در سبد خرید وجود ندارد")
        return


    header_cols = st.columns([1, 4, 2, 3])
    header_cols[0].markdown("**ردیف**")
    header_cols[1].markdown("**نام محصول**")
    header_cols[2].markdown("**تعداد**")
    header_cols[3].markdown("**ویرایش**")


    for idx, (product, count) in enumerate(st.session_state.purchase_list.items(), start=1):
        cols = st.columns([1, 4, 2, 3])
        cols[0].markdown(f"{to_persian_num(idx)}")
        cols[1].markdown(f"{product}")
        cols[2].markdown(f"{to_persian_num(count)}")

        with cols[3]:
            btn_cols = st.columns([1, 1, 1])
            btn_cols[0].button(
                "➖",
                key=f"dec_{product}",
                help="کاهش تعداد",
                use_container_width=True,
                on_click=modify_quantity,
                args=(product, -1)
            )
            btn_cols[1].button(
                "➕", 
                key=f"inc_{product}",
                help="افزایش تعداد",
                use_container_width=True,
                on_click=modify_quantity,
                args=(product, 1)
            )
            btn_cols[2].button(
                "❌", 
                key=f"del_{product}",
                help="حذف محصول",
                use_container_width=True,
                on_click=delete_product,
                args=(product,)
            )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "🔄 شروع دوباره عملیات خرید", 
            use_container_width=True,
            on_click=lambda: [
                st.session_state.update({
                    'purchase_started': False,
                    'running': False,
                    'purchase_list': {},
                    'tracked_objects': {},
                    'final_list': None
                }), None
            ]
        )

    with col2:
        if st.button("✅ ثبت نهایی خرید", use_container_width=True):
            st.session_state.final_list = dict(st.session_state.purchase_list)
            try:
                response = requests.post(
                    "http://localhost:5001/submit",
                    json=st.session_state.final_list,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    st.success("✅ لیست خرید با موفقیت ثبت شد!")
                    components.html(
                        f"""
                        <div style=\"text-align: center; animation: fadeIn 0.5s ease;\">   
                            <h3>✅ خرید با موفقیت ثبت شد!</h3>
                            <p>برای ادامه خرید و پرداخت به پنل کاربری قسمت سفارش جاری مراجعه کنید</p>
                        </div>
                        <script>
                            setTimeout(function() {{ window.close(); }}, 1000);
                        </script>
                        <style>
                            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px);}} to {{ opacity: 1; transform: translateY(0);}} }}
                        </style>
                        """, height=150
                    )
                    time.sleep(1)
                    os.kill(os.getpid(), signal.SIGTERM)    
                else:
                    st.error(f"خطا در ثبت خرید! کد خطا: {response.status_code}")
                    try:
                        st.json(response.json())
                    except ValueError:
                        st.warning("❗️ پاسخ سرور JSON معتبر نیست")
                        st.text(response.text)
            except Exception as e:
                st.error(f"خطا در ارتباط با سرور: {str(e)}")




def main():
    st.set_page_config(
        page_title="سیستم خرید هوشمند",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    add_custom_css()
    init_session_state()
    

    generate_wave_top()

    if not st.session_state.purchase_started:
        show_initial_page()
    else:
        if st.session_state.running:
            run_camera()
        else:
            show_final_page()
            

    generate_wave_bottom()

if __name__ == "__main__":
    main()