
import streamlit as st
import pandas as pd
from costimaize_v8_main_full import CostimAIzeOrchestrator
import fitz  # PyMuPDF
import docx2txt

st.set_page_config(page_title="CostimAIze V8.1", layout="wide")

# --- الشعار والهوية ---
st.image("logo.png", width=130)
st.markdown(
    "<h4 style='text-align: center; color: #5A6E3D;'>Estimate Smarter. Analyze Deeper.</h4>",
    unsafe_allow_html=True
)
st.markdown("---")

if "sow_text" not in st.session_state:
    st.session_state["sow_text"] = ""
if "inquiries" not in st.session_state:
    st.session_state["inquiries"] = []
if "estimation_result" not in st.session_state:
    st.session_state["estimation_result"] = {}

service = st.radio("Select Service Type:", ["", "Turnkey Cost Estimation", "Bid Analysis"], horizontal=True)

if service == "Turnkey Cost Estimation":
    st.subheader("Upload Scope of Work (SOW) File")
    sow_file = st.file_uploader("PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

    if st.button("Run Scope Analyzer") and sow_file:
        if sow_file.name.endswith(".pdf"):
            doc = fitz.open(stream=sow_file.read(), filetype="pdf")
            st.session_state["sow_text"] = "".join([page.get_text() for page in doc])
        elif sow_file.name.endswith(".docx"):
            st.session_state["sow_text"] = docx2txt.process(sow_file)
        elif sow_file.name.endswith(".txt"):
            st.session_state["sow_text"] = sow_file.read().decode("utf-8")

        orchestrator = CostimAIzeOrchestrator()
        st.session_state["inquiries"] = orchestrator.detect_inquiries(st.session_state["sow_text"])
        st.success("SOW loaded and analyzed.")

    if st.session_state["inquiries"]:
        st.subheader("Smart Technical Inquiries:")
        for q in st.session_state["inquiries"]:
            st.markdown(f"- {q}")
        st.info("Please review the inquiries before proceeding.")

    if st.button("Run Smart Turnkey Estimation") and st.session_state["sow_text"]:
        orchestrator = CostimAIzeOrchestrator()
        result = orchestrator.run_estimation(st.session_state["sow_text"])
        if result:
            st.session_state["estimation_result"] = result
            st.success("Estimation completed.")

if st.session_state["estimation_result"]:
    st.markdown("---")
    st.subheader("Estimation Output")
    st.write(st.session_state["estimation_result"])

    st.markdown("---")
    st.subheader("Dashboard")
    st.markdown("Coming soon: analytics, risk profiling, component comparisons.")
