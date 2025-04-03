
import streamlit as st
import base64
import pandas as pd
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze V8", layout="wide")

# تغيير خلفية الصفحة باستخدام CSS
st.markdown("""
    <style>
        body {
            background-color: #f8f5f0;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# تضمين صورة الشعار المحلي
st.image("logo.png", width=130)

# عبارة الهوية النصية المختصرة تحت الشعار
st.markdown(
    "<h4 style='text-align: center; color: #5A6E3D;'>Estimate Smarter. Analyze Deeper.</h4>",
    unsafe_allow_html=True
)

st.markdown("---")

# اختيار نوع الخدمة
service = st.radio("اختر نوع الخدمة التي ترغب بها:", ["", "تقدير تكلفة", "تحليل سعري لعطاء"], horizontal=True)

if service == "تقدير تكلفة":
    st.markdown("### تحميل ملف نطاق العمل (SOW)")
    sow_file = st.file_uploader("ارفع ملف نطاق العمل بصيغة PDF أو DOCX أو TXT", type=["pdf", "docx", "txt"])

    st.markdown("### معلومات المشروع")
    col1, col2 = st.columns(2)
    with col1:
        project_type = st.selectbox("نوع المشروع", ["", "محطة", "كابلات", "خطوط هوائية", "أخرى"])
        location = st.text_input("الموقع الجغرافي")
    with col2:
        duration = st.text_input("فترة التنفيذ", placeholder="مثال: 18 شهر")
        project_code = st.text_input("رقم المشروع (اختياري)")

    if project_type == "أخرى":
        other_description = st.text_input("يرجى وصف نوع المشروع")

    misc_notes = st.text_area("معلومات أخرى (اختياري)", height=100)

    if st.button("تشغيل التقدير الذكي") and sow_file:
        st.success("جاري تنفيذ التقدير عبر CostimAIzeOrchestrator ...")
        orchestrator = CostimAIzeOrchestrator()
        orchestrator.run_estimation("Placeholder SOW text", [])  # ربط لاحق لاحقًا

elif service == "تحليل سعري لعطاء":
    st.markdown("### تحميل ملف نطاق العمل (SOW)")
    sow_file = st.file_uploader("ارفع ملف نطاق العمل بصيغة PDF أو DOCX أو TXT", type=["pdf", "docx", "txt"])

    st.markdown("### تحميل جدول الأسعار المقدم من المقاول")
    bid_file = st.file_uploader("ارفع جدول الأسعار (CSV)", type=["csv"])

    if st.button("تشغيل التحليل السعري") and sow_file and bid_file:
        st.success("جاري تحليل العرض باستخدام CostimAIze V8...")

# أرشيف الأسعار التاريخية
st.markdown("---")
st.subheader("أرشيف الأسعار التاريخية")
archive_file = st.file_uploader("ارفع ملف أسعار تاريخية جديد (CSV)", type=["csv"])
if archive_file:
    st.success("تم حفظ الملف في الأرشيف الداخلي.")

# Dashboard
st.markdown("---")
st.subheader("لوحة المتابعة Dashboard")
st.markdown("يتم عرض النتائج والتوصيات هنا بعد التشغيل الفعلي.")
