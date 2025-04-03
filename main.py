
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

# تهيئة session state إذا لم يكن موجود
if "sow_text" not in st.session_state:
    st.session_state["sow_text"] = ""
if "inquiries" not in st.session_state:
    st.session_state["inquiries"] = []
if "estimation_result" not in st.session_state:
    st.session_state["estimation_result"] = {}

# اختيار نوع الخدمة
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

    # الزر الأول: قراءة الملف وتحليل الاستفسارات
    if st.button("تشغيل مرحلة الفحص الذكي") and sow_file:
        try:
            if sow_file.name.endswith(".pdf"):
                doc = fitz.open(stream=sow_file.read(), filetype="pdf")
                st.session_state["sow_text"] = "".join([page.get_text() for page in doc])
            elif sow_file.name.endswith(".docx"):
                st.session_state["sow_text"] = docx2txt.process(sow_file)
            elif sow_file.name.endswith(".txt"):
                st.session_state["sow_text"] = sow_file.read().decode("utf-8")

            st.success("تم قراءة نطاق العمل بنجاح. يتم الآن تحليل الاستفسارات الذكية...")
            orchestrator = CostimAIzeOrchestrator()
            st.session_state["inquiries"] = orchestrator.detect_inquiries(st.session_state["sow_text"])

        except Exception as e:
            st.error(f"خطأ أثناء معالجة الملف: {e}")

    # عرض الاستفسارات إن وُجدت
    if st.session_state["inquiries"]:
        st.markdown("### الاستفسارات الفنية الذكية:")
        for q in st.session_state["inquiries"]:
            st.markdown(f"- {q}")
        st.info("يرجى مراجعة هذه الاستفسارات قبل إصدار التقدير.")

    # الزر الثاني: تشغيل التقدير
    if st.button("تشغيل التقدير بعد مراجعة الاستفسارات") and st.session_state["sow_text"]:
        try:
            orchestrator = CostimAIzeOrchestrator()
            result = orchestrator.run_estimation(st.session_state["sow_text"], [])
            if result:
                st.session_state["estimation_result"] = result
                st.success("تم تنفيذ التقدير بنجاح.")
            else:
                st.warning("تم تنفيذ التقدير ولكن لم يتم توليد نتائج.")

        except Exception as e:
            st.error(f"حدث خطأ أثناء التقدير: {e}")

# --------------------------------------------------
# عرض النتائج بعد التقدير
if st.session_state["estimation_result"]:
    st.markdown("---")
    st.subheader("النتائج الذكية")
    st.write(st.session_state["estimation_result"])

    st.markdown("---")
    st.subheader("لوحة المتابعة Dashboard")
    st.markdown("يتم عرض التوصيات والتحليلات هنا.")

