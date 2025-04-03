
import streamlit as st
import base64
import os
import openai
import fitz  # PyMuPDF
import docx2txt
from costimaize_v8_main_full import CostimAIzeOrchestrator

# Page Configuration
st.set_page_config(page_title="CostimAIze V8", layout="wide")

# Inject Logo and Visual Identity
st.markdown(
    '''
    <div style='text-align: center; margin-bottom: 30px;'>
        <img src="https://i.imgur.com/XQ8hK1T.png" width="160" />
        <h1 style='color:#2C3E50;'>CostimAIze</h1>
        <h4 style='color:#7F8C8D;'>Estimate Smarter. Analyze Deeper.</h4>
    </div>
    ''',
    unsafe_allow_html=True
)

st.subheader("Upload Scope of Work (SOW) File")
uploaded_file = st.file_uploader("Drag and drop file here", type=["pdf", "docx", "txt"])

with st.expander("Project Information"):
    project_type = st.selectbox("Project Type", ["Substation", "Cables", "Overhead Line", "Other"])
    location = st.text_input("Project Location")
    duration = st.text_input("Execution Duration (in months)", placeholder="e.g., 24")
    contract_type = st.selectbox("Contract Type (Mandatory)", ["Lump Sum Turnkey", "Unit Rate", "LSTK & Unit Rate"])
    additional_notes = st.text_area("Additional Notes (Optional)")

sow_text = ""
results = {}
if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    if file_ext == "pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        sow_text = "\n".join([page.get_text() for page in doc])
    elif file_ext == "docx":
        sow_text = docx2txt.process(uploaded_file)
    elif file_ext == "txt":
        sow_text = uploaded_file.read().decode("utf-8")

    if sow_text:
        st.success("SOW uploaded successfully.")
        if st.button("Run Smart Turnkey Estimation"):
            st.info("Executing estimation...")
            orchestrator = CostimAIzeOrchestrator()
            results = orchestrator.run_estimation(sow_text)
            st.success("Estimation complete.")

if results:
    st.subheader("Estimation Output")
    st.json(results)

    st.subheader("Dashboard")
    import matplotlib.pyplot as plt
    import pandas as pd
    if "Breakdown" in results:
        labels = list(results["Breakdown"].keys())
        values = [float(x.replace("SAR", "").replace(",", "").strip()) for x in results["Breakdown"].values()]
        df = pd.DataFrame({"Component": labels, "Cost": values})
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df["Component"], df["Cost"], color="#2C3E50")
        ax.set_ylabel("Cost (SAR)")
        ax.set_title("Cost Breakdown")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
else:
    st.info("Please upload a valid SOW file and run the estimation.")
