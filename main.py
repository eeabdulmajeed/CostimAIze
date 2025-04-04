
import streamlit as st
import os
from costimaize_v8_main_full import CostimAIzeOrchestrator

# Initialize orchestrator
orch = CostimAIzeOrchestrator()

st.image("https://i.imgur.com/XQ8hK1T.png", width=120)
st.markdown("## CostimAIze")
st.markdown("**Estimate Smarter. Analyze Deeper.**")

service = st.selectbox("Select Service", ["Project Cost Estimation", "Bid Price Analysis", "Upload Historical Prices"])

if service == "Project Cost Estimation":
    st.subheader("Upload Scope of Work (SOW) File")
    sow_file = st.file_uploader("Drag and drop file here", type=["pdf", "docx", "txt"])
    if sow_file:
        sow_text = orch.extract_text(sow_file)
        st.session_state["sow_text"] = sow_text
        st.success("SOW uploaded successfully.")

    if "sow_text" in st.session_state:
        if st.button("Run Scope Analyzer"):
            scope = orch.analyze_scope(st.session_state["sow_text"])
            st.session_state["scope"] = scope
            st.success("Scope analyzed.")

        if st.button("Run Smart Technical Inquiries"):
            inquiries = orch.detect_inquiries(st.session_state["sow_text"])
            st.session_state["inquiries"] = inquiries
            if inquiries:
                st.error("Technical Inquiries Found:")
                for q in inquiries:
                    st.write(f"- {q}")
            else:
                st.info("No technical inquiries detected.")

        if st.button("Run Smart Turnkey Estimation"):
            result = orch.run_estimation(st.session_state["sow_text"])
            st.session_state["result"] = result
            st.success("Estimation complete.")

    if "result" in st.session_state:
        st.subheader("Estimation Output")
        st.json(st.session_state["result"])

elif service == "Bid Price Analysis":
    st.info("Bid Price Analysis is under development.")

elif service == "Upload Historical Prices":
    st.info("Upload feature coming soon.")
