
import streamlit as st
import fitz
import docx2txt
import pandas as pd
import matplotlib.pyplot as plt
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze V8.3", layout="wide")

st.image("logo.png", width=120)
st.markdown("<h4 style='text-align: center; color: #5A6E3D;'>Estimate Smarter. Analyze Deeper.</h4>", unsafe_allow_html=True)
st.markdown("---")

mode = st.selectbox("Select Service", ["-- Select --", "Turnkey Cost Estimation", "Bid Price Analysis", "Upload Historical Prices"])

if "sow_text" not in st.session_state:
    st.session_state["sow_text"] = ""
if "result" not in st.session_state:
    st.session_state["result"] = {}
if "inquiries" not in st.session_state:
    st.session_state["inquiries"] = []

if mode == "Turnkey Cost Estimation":
    st.subheader("1. Upload Scope of Work")
    sow_file = st.file_uploader("Upload SOW File (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    st.subheader("2. Project Information")
    col1, col2 = st.columns(2)
    with col1:
        p_type = st.selectbox("Project Type", ["Substation", "Cables", "Overhead Lines", "Other"])
        location = st.text_input("Project Location")
    with col2:
        duration = st.text_input("Execution Duration (months)", placeholder="e.g. 24")
        contract_type = st.selectbox("Contract Type *", ["", "Lump Sum Turnkey", "Unit Rate", "LSTK & Unit Rate"])

    st.markdown("### Optional")
    notes = st.text_area("Additional Notes")

    if sow_file and contract_type:
        if st.button("Run Scope Analyzer"):
            if sow_file.name.endswith("pdf"):
                doc = fitz.open(stream=sow_file.read(), filetype="pdf")
                st.session_state["sow_text"] = "".join([p.get_text() for p in doc])
            elif sow_file.name.endswith("docx"):
                st.session_state["sow_text"] = docx2txt.process(sow_file)
            elif sow_file.name.endswith("txt"):
                st.session_state["sow_text"] = sow_file.read().decode("utf-8")

            orch = CostimAIzeOrchestrator()
            orch.set_context(p_type, location, duration, contract_type, notes)
            st.session_state["inquiries"] = orch.detect_inquiries(st.session_state["sow_text"])
            st.success("Scope analyzed successfully.")

        if st.session_state["inquiries"]:
            st.subheader("Technical Inquiries Detected")
            for q in st.session_state["inquiries"]:
                st.markdown(f"- {q}")
        elif st.session_state["sow_text"]:
            st.info("No technical inquiries detected.")

        if st.button("Run Smart Turnkey Estimation") and not st.session_state["result"]:
            orch = CostimAIzeOrchestrator()
            st.session_state["result"] = orch.run_estimation(st.session_state["sow_text"])

    if st.session_state["result"]:
        st.subheader("Estimation Result")
        st.json(st.session_state["result"])
        if "Breakdown" in st.session_state["result"]:
            st.subheader("Dashboard")
            labels = list(st.session_state["result"]["Breakdown"].keys())
            values = [float(x.replace("SAR", "").replace(",", "")) for x in st.session_state["result"]["Breakdown"].values()]
            df = pd.DataFrame({"Component": labels, "Cost": values})
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(df["Component"], df["Cost"], color="#5A6E3D")
            plt.xticks(rotation=45)
            st.pyplot(fig)

elif mode == "Bid Price Analysis":
    st.subheader("Upload Files for Bid Price Analysis")
    sow_file = st.file_uploader("Upload SOW", type=["pdf", "docx", "txt"])
    bid_file = st.file_uploader("Upload Contractor Price Table (CSV/XLSX/XLS)", type=["csv", "xlsx", "xls"])
    if sow_file and bid_file:
        st.warning("Bid Price Analysis is under development.")

elif mode == "Upload Historical Prices":
    st.subheader("Upload Historical Price Tables")
    hist_file = st.file_uploader("Upload CSV/XLSX/XLS File for Archiving", type=["csv", "xlsx", "xls"])
    if hist_file:
        try:
            if hist_file.name.endswith("csv"):
                df_hist = pd.read_csv(hist_file)
            else:
                df_hist = pd.read_excel(hist_file)
            st.success("File uploaded and stored successfully.")
            st.dataframe(df_hist.head())
        except Exception as e:
            st.error(f"Failed to process historical file: {e}")
