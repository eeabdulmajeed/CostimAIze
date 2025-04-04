
import streamlit as st
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze", layout="wide")

st.markdown(
    '''
    <div style='text-align: center; margin-bottom: -20px;'>
        <img src="https://i.imgur.com/XQ8hK1T.png" width="160"/>
        <h1 style='color:#2C3E50;'>CostimAIze</h1>
        <h4 style='color:#7F8C8D;'>Estimate Smarter. Analyze Deeper.</h4>
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("---")

orch = CostimAIzeOrchestrator()
service = st.selectbox("Select Service", ["Project Cost Estimation", "Bid Price Analysis", "Upload Historical Prices"])

if service == "Project Cost Estimation":
    st.subheader("Upload Scope of Work")
    sow_file = st.file_uploader("Upload SOW (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    if sow_file:
        text = orch.extract_text(sow_file)
        st.session_state["sow_text"] = text
        st.success("SOW uploaded successfully.")

    if "sow_text" in st.session_state:
        if st.button("Run Scope Analyzer"):
            scope = orch.analyze_scope(st.session_state["sow_text"])
            st.write(scope)

        if st.button("Run Smart Technical Inquiries"):
            inquiries = orch.detect_inquiries(st.session_state["sow_text"])
            if inquiries:
                st.warning("Technical Inquiries:")
                for iq in inquiries:
                    st.text(iq)

        if st.button("Run Smart Turnkey Estimation"):
            try:
                result = orch.run_estimation(st.session_state["sow_text"])
                st.session_state["result"] = result
                st.success("Estimation complete.")
                st.json(result)
            except Exception as e:
                st.error(str(e))

elif service == "Bid Price Analysis":
    st.subheader("Bid Price Analysis (Coming soon...)")

elif service == "Upload Historical Prices":
    st.subheader("Upload CSV/XLSX Historical Price Table")
    st.info("Upload with metadata to activate internal usage.")

