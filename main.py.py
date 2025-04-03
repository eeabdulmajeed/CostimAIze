
import streamlit as st
import pandas as pd
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze V8", layout="centered")

# --- الشعار والهوية ---
st.image("https://i.imgur.com/XQ8hK1T.png", width=200)  # ضع رابط شعارك الحقيقي هنا
st.markdown("""
<h1 style='text-align: center; color: #2C3E50;'>CostimAIze</h1>
<h4 style='text-align: center; color: #7F8C8D;'>Powered by AI • Smart Cost Estimation & Bid Analysis</h4>
""", unsafe_allow_html=True)

st.markdown("---")

# --- اختيار نوع الخدمة ---
st.subheader("اختر نوع الخدمة")
service = st.selectbox("", ["اختر...", "تقدير تكلفة", "تحليل سعري لعطاء"])

# --- واجهة تقدير تكلفة ---
if service == "تقدير تكلفة":
    st.markdown("### تحميل ملف نطاق العمل (SOW)")
    sow_file = st.file_uploader("ارفع ملف نطاق العمل بصيغة PDF أو DOCX أو TXT", type=["pdf", "docx", "txt"])

    st.markdown("### معلومات المشروع")
    col1, col2 = st.columns(2)
    with col1:
        project_type = st.text_input("نوع المشروع", placeholder="مثال: 132kV Substation")
        location = st.text_input("الموقع")
    with col2:
        year = st.text_input("سنة التنفيذ")
        project_code = st.text_input("رقم المشروع (اختياري)")

    st.markdown("### الأسعار التاريخية")
    hist_file = st.file_uploader("ارفع جدول أسعار تاريخية (CSV)", type=["csv"])

    if st.button("تشغيل التقدير الذكي") and sow_file:
        st.success("تم تنفيذ التقدير بنجاح. سيتم ربط النتائج مع CostimAIzeOrchestrator.")

# --- واجهة تحليل سعري ---
elif service == "تحليل سعري لعطاء":
    st.markdown("### تحميل نطاق العمل")
    sow_file = st.file_uploader("ارفع ملف نطاق العمل بصيغة PDF أو DOCX أو TXT", type=["pdf", "docx", "txt"])

    st.markdown("### تحميل جدول الأسعار المقدم من المقاول")
    bid_file = st.file_uploader("ارفع جدول الأسعار (CSV)", type=["csv"])

    if st.button("تشغيل التحليل الذكي") and sow_file and bid_file:
        st.success("تم تحليل العرض بنجاح. سيتم عرض التفاصيل لاحقًا.")

# --- صفحة أرشفة الأسعار التاريخية ---
st.markdown("---")
st.subheader("أرشيف الأسعار التاريخية")
archive_file = st.file_uploader("ارفع ملف أسعار تاريخية جديد (CSV)", type=["csv"])
if archive_file:
    st.success("تم حفظ الملف في الأرشيف الداخلي.")

# --- Dashboard مبدئي ---
st.markdown("---")
st.subheader("لوحة المتابعة Dashboard")
st.markdown("يتم عرض النتائج والتوصيات هنا بعد التشغيل الفعلي.")
