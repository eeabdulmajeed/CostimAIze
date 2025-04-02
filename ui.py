import streamlit as st


def show_estimation_ui():
    st.header("تقدير تكلفة مشروع جديد")
    st.write("يرجى رفع ملف نطاق العمل ليقوم الذكاء بتحليله وتقدير تكلفة التنفيذ.")

    uploaded_file = st.file_uploader("رفع نطاق العمل (PDF)", type=["pdf"], key="sow_pdf")

    if uploaded_file:
        st.success("تم رفع الملف بنجاح.")
        if st.button("ابدأ التقدير"):
            st.info("يتم الآن تنفيذ التحليل الذكي... (سيتم ربطه مع estimator.py)")


def show_analysis_ui():
    st.header("تحليل سعر عطاء مقدم")
    st.write("يرجى رفع الملفات المطلوبة لتحليل العرض المقدم من المقاول.")

    sow_file = st.file_uploader("رفع نطاق العمل (PDF)", type=["pdf"], key="sow_analysis")
    price_sheet = st.file_uploader("رفع جدول الأسعار (Excel)", type=["xls", "xlsx"], key="price_sheet")
    reference_price = st.file_uploader("رفع سعر تاريخي مرجعي (اختياري)", type=["xls", "xlsx"], key="ref_price")

    if sow_file and price_sheet:
        st.success("تم رفع الملفات بنجاح.")
        if st.button("ابدأ تحليل العطاء"):
            st.info("يتم الآن تحليل السعر... (سيتم ربطه مع analyzer.py و estimator.py)")
