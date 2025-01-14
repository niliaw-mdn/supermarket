import cv2
import streamlit as st
from ultralytics import YOLO
from collections import defaultdict

# بارگذاری مدل YOLO
yolo = YOLO('best.pt')

# استفاده از session_state برای ذخیره detected_objects و active_objects
if "detected_objects" not in st.session_state:
    st.session_state.detected_objects = {}

if "active_objects" not in st.session_state:
    st.session_state.active_objects = defaultdict(int)  # شامل شیء و تایمر مرتبط با آن

# تنظیمات مربوط به زمان ماندگاری اشیاء
FRAME_LIFETIME = 10  # تعداد فریم‌هایی که یک شیء می‌تواند غیرفعال بماند

def video_processing():
    # تغییرات detected_objects را در session_state ذخیره می‌کنیم
    detected_objects = st.session_state.detected_objects
    active_objects = st.session_state.active_objects

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("وب‌کم در دسترس نیست!")
        return

    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("عدم دریافت فریم از وب‌کم!")
            break

        # شناسایی اشیاء با استفاده از متد predict
        results = yolo(frame)

        # لیستی برای اشیاء موجود در این فریم
        current_objects = set()

        # نتایج YOLO شامل boxes و names است
        for result in results:
            # استخراج جعبه‌های شناسایی‌شده و اسامی
            boxes = result.boxes
            names = result.names

            # پردازش جعبه‌ها و برچسب‌ها
            for i, box in enumerate(boxes):
                # استخراج مختصات جعبه‌ها
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # رسم Bounding Box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

                # نام شیء را در کنار جعبه بنویسید
                label = names[int(box.cls)]
                current_objects.add(label)

                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # مدیریت اشیاء فعال با تایمر
        for obj in current_objects:
            if obj not in active_objects:  # شیء جدید است
                if obj in detected_objects:
                    detected_objects[obj] += 1
                else:
                    detected_objects[obj] = 1
            active_objects[obj] = FRAME_LIFETIME  # ریست کردن تایمر

        # کاهش تایمر اشیاء فعال
        to_remove = []
        for obj in active_objects:
            if obj not in current_objects:
                active_objects[obj] -= 1
                if active_objects[obj] <= 0:  # اگر تایمر به پایان برسد
                    to_remove.append(obj)

        # حذف اشیاء غیرفعال از لیست
        for obj in to_remove:
            del active_objects[obj]

        # نمایش فریم
        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

        # بررسی وضعیت دکمه پایان عملیات
        if st.session_state.stop_processing:
            break

    cap.release()
    cv2.destroyAllWindows()

# رابط کاربری با Streamlit
def streamlit_app():
    st.title("شناسایی اشیاء با YOLOv11")
    st.write("این اپلیکیشن از YOLOv11 برای شناسایی اشیاء از دوربین وب استفاده می‌کند.")
    st.write("برای توقف نمایش ویدیو، بر روی دکمه 'پایان عملیات' کلیک کنید.")

    # اگر stop_processing در session_state وجود ندارد، آن را تنظیم می‌کنیم
    if "stop_processing" not in st.session_state:
        st.session_state.stop_processing = False

    # دکمه‌ها برای شروع و پایان شناسایی
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.stop_processing:
            if st.button("شروع شناسایی", key="start_button"):
                st.session_state.stop_processing = False
                video_processing()

    with col2:
        if st.session_state.stop_processing:
            st.write("پردازش متوقف شد.")
        else:
            if st.button("پایان عملیات", key="end_button"):
                st.session_state.stop_processing = True
                st.write("اشیاء شناسایی‌شده و تعداد آن‌ها:", st.session_state.detected_objects)

    # نمایش لیست اشیاء شناسایی‌شده به‌روزرسانی‌شده به‌صورت ریل تایم
    if not st.session_state.stop_processing:
        st.write("اشیاء شناسایی‌شده ریل تایم:")
        st.write(st.session_state.detected_objects)

# اجرای اپلیکیشن
if __name__ == "__main__":
    streamlit_app()
