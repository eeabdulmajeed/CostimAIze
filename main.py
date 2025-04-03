
import streamlit as st
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze", layout="wide")

st.image("https://i.imgur.com/XQ8hK1T.png", width=120)
st.markdown("## Estimate Smarter. Analyze Deeper.")

st.markdown("---")

# اختيار نوع الخدمة
service = st.selectbox("Select Service", [
    "Project Cost Estimation",
    "Bid Price Analysis",
    "Upload Historical Prices"
])

orch = CostimAIzeOrchestrator()

if service == "Project Cost Estimation":
    st.subheader("Upload Scope of Work (SOW) File")
    sow_file = st.file_uploader("Upload SOW", type=["pdf", "docx", "txt"])
    if sow_file:
        st.success("SOW uploaded successfully.")
        content = sow_file.read().decode("utf-8") if sow_file.type == "text/plain" else ""
        st.session_state["sow_text"] = content
        if st.button("Run Scope Analyzer"):
            st.session_state["scope"] = orch.analyze_scope(content)
            st.success("Scope analyzed.")
        if st.button("Run Smart Turnkey Estimation"):
            st.session_state["result"] = orch.run_estimation(content)
            st.success("Estimation complete.")
            st.json(st.session_state["result"])

elif service == "Bid Price Analysis":
    st.info("Bid Price Analysis is under development.")

elif service == "Upload Historical Prices":
    st.info("Upload feature coming soon.")
