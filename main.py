
import streamlit as st
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze V8", layout="wide")
st.title("CostimAIze V8 - Smart Estimation Engine")

st.markdown("""---""")
st.subheader("1. أدخل نطاق العمل (SOW)")
sow_input = st.text_area("مثال: Supply and install 2 Transformers, GIS, Protection and Control systems...", height=250)

st.markdown("""---""")
st.subheader("2. ارفع ملف الأسعار التاريخية (اختياري)")
uploaded_file = st.file_uploader("صيغة CSV فقط: columns = type, component, price", type=["csv"])
historical_data = []

if uploaded_file:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    for _, row in df.iterrows():
        historical_data.append({
            "type": row["type"],
            "component": row["component"],
            "price": row["price"]
        })

if st.button("تشغيل التقدير الذكي") and sow_input:
    orchestrator = CostimAIzeOrchestrator()
    orchestrator.run_estimation(sow_input, historical_data)
