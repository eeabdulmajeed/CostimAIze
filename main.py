
import streamlit as st
import pandas as pd
from costimaize_v8_main_full import CostimAIzeOrchestrator
import fitz  # PyMuPDF
import docx2txt

st.set_page_config(page_title="CostimAIze V8", layout="wide")

# --- الشعار والهوية ---
st.image("logo.png", width=130)
st.markdown(
    "<h4 style='text-align: center; color: #5A6E3D;'>Estimate Smarter. Analyze Deeper.</h4>",
    unsafe_allow_html=True
)
st.markdown("---")

# حالات تشغيل متعددة
sow_text = ""
inquiries = []
estimation_result = None

service = st.radio("اختر نوع الخدمة التي ترغب بها:", ["", "تقدير تكلفة", "تحليل سعري لعطاء"], horizontal=True)

# --------------------------------------------------
# تقدير تكلفة
if service == "تقدير تكلفة":
    st.markdown("### تحميل ملف نطاق العمل (SOW)")
    sow_file = st.file_uploader("ارفع ملف بصيغة PDF أو DOCX أو TXT", type=["pdf", "docx", "txt"])

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

    if st.button("تشغيل مرحلة الفحص الذكي") and sow_file:
        if sow_file.name.endswith(".pdf"):
            doc = fitz.open(stream=sow_file.read(), filetype="pdf")
            for page in doc:
                sow_text += page.get_text()
        elif sow_file.name.endswith(".docx"):
            sow_text = docx2txt.process(sow_file)
        elif sow_file.name.endswith(".txt"):
            sow_text = sow_file.read().decode("utf-8")

        st.success("تم قراءة نطاق العمل بنجاح. يتم الآن تحليل الاستفسارات الذكية...")
        orchestrator = CostimAIzeOrchestrator()
        inquiries = orchestrator.detect_inquiries(sow_text)

    if inquiries:
        st.markdown("### الاستفسارات الفنية الذكية:")
        for q in inquiries:
            st.markdown(f"- {q}")

        st.info("يرجى مراجعة هذه الاستفسارات قبل إصدار التقدير.")

    if st.button("تشغيل التقدير بعد مراجعة الاستفسارات") and sow_text:
        orchestrator = CostimAIzeOrchestrator()
        estimation_result = orchestrator.run_estimation(sow_text, [])
        st.success("تم تنفيذ التقدير بنجاح.")

# --------------------------------------------------
# عرض النتائج بعد التقدير
if estimation_result:
    st.markdown("---")
    st.subheader("النتائج الذكية")
    st.write(estimation_result)

    st.markdown("---")
    st.subheader("لوحة المتابعة Dashboard")
    st.markdown("تُعرض التوصيات والتحليلات هنا.")
