
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

# حالة تشغيل التقدير
estimation_done = False
results = None

# اختيار نوع الخدمة
service = st.radio("اختر نوع الخدمة التي ترغب بها:", ["", "تقدير تكلفة", "تحليل سعري لعطاء"], horizontal=True)

# --------------------------------------------------
# تقدير تكلفة
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
        file_text = ""
        if sow_file.name.endswith(".pdf"):
            doc = fitz.open(stream=sow_file.read(), filetype="pdf")
            for page in doc:
                file_text += page.get_text()
        elif sow_file.name.endswith(".docx"):
            file_text = docx2txt.process(sow_file)
        elif sow_file.name.endswith(".txt"):
            file_text = sow_file.read().decode("utf-8")

        if file_text:
            st.success("تم قراءة ملف نطاق العمل بنجاح. يتم الآن تنفيذ التقدير...")
            orchestrator = CostimAIzeOrchestrator()
            results = orchestrator.run_estimation(file_text, [])
            estimation_done = True

# --------------------------------------------------
# تحليل سعري لعطاء
elif service == "تحليل سعري لعطاء":
    st.markdown("### تحميل ملف نطاق العمل (SOW)")
    sow_file = st.file_uploader("ارفع ملف نطاق العمل بصيغة PDF أو DOCX أو TXT", type=["pdf", "docx", "txt"])

    st.markdown("### تحميل جدول الأسعار المقدم من المقاول")
    bid_file = st.file_uploader("ارفع جدول الأسعار (CSV)", type=["csv"])

    if st.button("تشغيل التحليل السعري") and sow_file and bid_file:
        st.success("جاري تحليل العرض باستخدام CostimAIze V8...")

# --------------------------------------------------
# عرض النتائج فقط عند تنفيذ التقدير
if estimation_done and results:
    st.markdown("---")
    st.subheader("النتائج الذكية")
    st.write(results)

    st.markdown("---")
    st.subheader("لوحة المتابعة Dashboard")
    st.markdown("تُعرض التوصيات والتحليلات بعد التقدير.")

