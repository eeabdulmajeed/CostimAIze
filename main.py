
import streamlit as st
import fitz
import docx2txt
import pandas as pd
import matplotlib.pyplot as plt
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.set_page_config(page_title="CostimAIze V8.4", layout="wide")

st.image("logo.png", width=120)
st.markdown("<h4 style='text-align: center; color: #5A6E3D;'>Estimate Smarter. Analyze Deeper.</h4>", unsafe_allow_html=True)
st.markdown("---")

mode = st.selectbox("Select Service", ["-- Select --", "Project Cost Estimation", "Bid Price Analysis", "Upload Historical Prices"])

if "sow_text" not in st.session_state:
    st.session_state["sow_text"] = ""
if "result" not in st.session_state:
    st.session_state["result"] = {}
if "inquiries" not in st.session_state:
    st.session_state["inquiries"] = []
if "answers" not in st.session_state:
    st.session_state["answers"] = {}

if mode == "Project Cost Estimation":
    # ... [الكود الأساسي نفسه هنا لتقدير التكلفة] ...
    pass

elif mode == "Bid Price Analysis":
    st.subheader("Upload Files for Bid Price Analysis")
    sow_file = st.file_uploader("Upload SOW", type=["pdf", "docx", "txt"])
    bid_file = st.file_uploader("Upload Contractor Price Table (CSV/XLSX/XLS)", type=["csv", "xlsx", "xls"])
    if sow_file and bid_file:
        st.warning("Bid Price Analysis is under development.")
    else:
        st.info("Please upload both SOW and Bid Table to proceed.")

elif mode == "Upload Historical Prices":
    st.subheader("Upload Historical Price Tables")
    hist_file = st.file_uploader("Upload CSV/XLSX/XLS File for Archiving", type=["csv", "xlsx", "xls"])
    if hist_file:
        try:
            if hist_file.name.endswith("csv"):
                df_hist = pd.read_csv(hist_file)
            else:
                df_hist = pd.read_excel(hist_file, engine="openpyxl")
            st.success("File uploaded and stored successfully.")
            st.dataframe(df_hist.head())
        except Exception as e:
            st.error(f"Failed to process historical file: {e}")
