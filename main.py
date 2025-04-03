
import streamlit as st
import pandas as pd
from costimaize_v8_main_full import CostimAIzeOrchestrator
import fitz  # PyMuPDF
import docx2txt

st.set_page_config(page_title="CostimAIze V8.2", layout="wide")

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
if "contract_type" not in st.session_state:
    st.session_state["contract_type"] = ""

service = st.radio("Select Service Type:", ["", "Turnkey Cost Estimation", "Bid Analysis"], horizontal=True)

if service == "Turnkey Cost Estimation":
    st.subheader("Upload Scope of Work (SOW) File")
    sow_file = st.file_uploader("PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

    st.markdown("### Project Information")
    col1, col2 = st.columns(2)
    with col1:
        project_type = st.selectbox("Project Type", ["", "Substation", "Cables", "Overhead Lines", "Other"])
        location = st.text_input("Project Location")
    with col2:
        duration = st.text_input("Execution Duration (in months)", placeholder="e.g., 24")
        st.session_state["contract_type"] = st.selectbox("Contract Type (Mandatory)", ["", "Lump Sum Turnkey (LSTK)", "Unit Rate", "LSTK & Unit Rate"])

    if project_type == "Other":
        other_description = st.text_input("Describe Project Type")

    st.markdown("### Optional")
    misc_notes = st.text_area("Additional Notes", height=100)

    if st.button("Run Scope Analyzer") and sow_file and st.session_state["contract_type"]:
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

    st.subheader("Smart Technical Inquiries:")
    if st.session_state["inquiries"]:
        for q in st.session_state["inquiries"]:
            st.markdown(f"- {q}")
    else:
        st.info("No technical inquiries were detected.")

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
    df = pd.DataFrame.from_dict(st.session_state["estimation_result"].get("Breakdown", {}), orient="index", columns=["Estimated Cost"])
    st.bar_chart(df)
