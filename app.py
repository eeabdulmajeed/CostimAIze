import streamlit as st
from ui import show_estimation_ui, show_analysis_ui

st.set_page_config(
    page_title="CostimAIze | منصة تحليل وتقدير ذكي",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {background-color: #f9fafb;}
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

st.title("مرحباً بك في CostimAIze")
st.subheader("اختر الخدمة التي ترغب بتنفيذها")

option = st.radio(
    "",
    ["تقدير تكلفة مشروع جديد", "تحليل سعر عطاء مقدم"],
    index=0,
    horizontal=True,
    help="اختر الخدمة المناسبة لنطاق العمل المتوفر لديك"
)

st.markdown("---")

if option == "تقدير تكلفة مشروع جديد":
    show_estimation_ui()

elif option == "تحليل سعر عطاء مقدم":
    show_analysis_ui()
