import streamlit as st
from ui import show_estimation_ui, show_analysis_ui
from estimator import run_prudent_estimator

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
    st.header("تقدير تكلفة مشروع جديد")
    sow_file = st.file_uploader("رفع نطاق العمل (PDF أو TXT)", type=["pdf", "txt"])

    if sow_file and st.button("ابدأ التقدير"):
        with st.spinner("يتم الآن تحليل نطاق العمل وتشغيل الذكاء..."):
            result = run_prudent_estimator(sow_file)
            st.success("تم التقدير بنجاح")

            st.subheader("النتائج:")
            st.write(f"**السعر التقديري:** {result['السعر التقديري']}")
            st.write(f"**درجة الثقة:** {result['درجة الثقة']}")
            st.write("**عوامل الحذر:**")
            for factor in result['عوامل الحذر']:
                st.write(f"- {factor}")
            st.write("**شرح القرار:**")
            st.info(result['شرح القرار'])

elif option == "تحليل سعر عطاء مقدم":
    show_analysis_ui()

