import streamlit as st
import pandas as pd
import io
from costimaize_v8_main_full import CostimAIzeOrchestrator

# تعريف دالة مساعدة للتنزيل
def download_csv(df, label, filename):
    if not df.empty:
        st.download_button(
            label=label,
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=filename,
            mime="text/csv"
        )

# إعداد الصفحة
st.set_page_config(page_title="CostimAIze", layout="wide")

st.markdown(
    """
    <div style='text-align: center; margin-bottom: -20px;'>
        <img src="https://i.imgur.com/XQ8hK1T.png" width="160"/>
        <h1 style='color:#2C3E50;'>CostimAIze</h1>
        <h4 style='color:#7F8C8D;'>Estimate Smarter. Analyze Deeper.</h4>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

@st.cache_resource
def get_orchestrator():
    return CostimAIzeOrchestrator()

orch = get_orchestrator()
service = st.selectbox("Select Service", ["Project Cost Estimation", "Bid Price Analysis", "Upload Historical Prices"])

# قسم تقدير تكلفة المشروع
if service == "Project Cost Estimation":
    st.subheader("Upload Scope of Work")
    st.markdown("**Accepted formats:** PDF, DOCX, TXT. Minimum content: Scope, technical, and project keywords.")
    sow_file = st.file_uploader("Upload SOW (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    if sow_file:
        with st.spinner("Processing file..."):
            try:
                text = orch.extract_text(sow_file)
                st.session_state["sow_text"] = text
                st.session_state["is_valid"] = orch.validate_sow(text)
                st.success("SOW uploaded successfully." if st.session_state["is_valid"] else "File uploaded but may not meet minimum requirements.")
            except ValueError as e:
                st.error(str(e))

    if "sow_text" in st.session_state and st.session_state.get("is_valid"):
        inquiries = orch.detect_inquiries(st.session_state["sow_text"])
        st.session_state["inquiries"] = inquiries

        if inquiries:
            st.subheader("AI-Detected Questions & Gaps")
            st.session_state["responses"] = {}
            for i, iq in enumerate(inquiries):
                st.markdown(f"- **{iq['text']}** {'(Critical)' if iq['critical'] else ''}")
                response = st.text_input(f"Response to: {iq['text']}", key=f"response_{i}")
                st.session_state["responses"][iq['text']] = response

        col1, col2 = st.columns(2)
        with col1:
            p_type = st.selectbox("Project Type", ["Substation", "OHTL", "Cables", "Other"])
            location = st.text_input("Location")
            duration = st.number_input("Execution Duration (Months)", min_value=1)
        with col2:
            contract_type = st.selectbox("Contract Type", ["Lump Sum Turnkey", "Unit Rate", "LSTK & Unit Rate"])
            notes = st.text_area("Notes")

        critical_unanswered = any(iq["critical"] and not st.session_state["responses"].get(iq["text"]) for iq in inquiries)
        if st.button("Run Smart Turnkey Estimation") and not critical_unanswered:
            with st.spinner("Running estimation..."):
                try:
                    orch.set_context(p_type, location, duration, contract_type, notes, st.session_state["responses"])
                    result = orch.run_estimation(st.session_state["sow_text"])
                    st.session_state["result"] = result
                    st.success("Estimation complete.")

                    summary_df = pd.DataFrame(list(result.items()), columns=["Metric", "Value"])
                    st.table(summary_df)

                    download_csv(summary_df, "Download Estimation Result as CSV", "estimation_result.csv")
                    if "Breakdown" in result:
                        breakdown_df = pd.DataFrame(result["Breakdown"].items(), columns=["Component", "Estimated Cost"])
                        download_csv(breakdown_df, "Download Breakdown as CSV", "breakdown.csv")

                    st.subheader("Smart AI Recommendations")
                    if result.get("Used Historical Model") is False:
                        st.warning("لم يتم استخدام بيانات تاريخية - قد تكون النتائج أقل دقة.")
                    if result.get("Model Confidence") and float(str(result["Model Confidence"]).replace('%', '')) < 80:
                        st.warning("نموذج الذكاء غير واثق تمامًا من النتائج – ننصح بمراجعة البيانات التاريخية.")
                    if result.get("Adjusted for Inquiry Gaps"):
                        st.warning(result["Adjusted for Inquiry Gaps"])

                    st.subheader("AI Historical Data Analysis")
                    st.markdown(f"**Used Historical Model:** {result.get('Used Historical Model', 'N/A')}")
                    st.markdown(f"**Historical Data Size:** {result.get('Historical Data Size', 'N/A')}")
                    st.markdown(f"**Model Confidence:** {result.get('Model Confidence', 'N/A')}")
                except Exception as e:
                    st.error(f"Estimation failed: {str(e)}")
        elif critical_unanswered:
            st.warning("Please respond to all critical inquiries before running the estimation.")
    elif "sow_text" in st.session_state and not st.session_state.get("is_valid"):
        st.error("The uploaded file does not meet minimum project scope requirements.")

# قسم تحليل أسعار العروض
elif service == "Bid Price Analysis":
    st.subheader("Bid Price Analysis")
    bid_sow = st.file_uploader("Upload Scope of Work for Bid", type=["pdf", "docx", "txt"], key="bid_sow")
    bid_table = st.file_uploader("Upload Contractor's Price Table (CSV)", type=["csv"], key="bid_prices")

    if bid_sow and bid_table:
        try:
            with st.spinner("Analyzing bid..."):
                sow_text = orch.extract_text(bid_sow)
                df = pd.read_csv(bid_table)
                required = {"description", "quantity", "unit_price"}
                if not required.issubset(df.columns):
                    st.error("CSV must include: description, quantity, unit_price")
                else:
                    contractor_data = df.to_dict(orient='records')
                    analysis = orch.analyze_bid(sow_text, contractor_data)
                    if "error" in analysis:
                        st.error(analysis["error"])
                    else:
                        st.success("Bid analysis completed.")
                        st.write("Summary:", analysis["summary"])
                        st.write("Detailed Analysis:")
                        analysis_df = pd.DataFrame(analysis["analysis"])
                        st.dataframe(analysis_df)
                        download_csv(analysis_df, "Download Bid Analysis as CSV", "bid_analysis.csv")
        except Exception as e:
            st.error(f"Failed to analyze bid: {str(e)}")
    else:
        st.info("Please upload both SOW and Contractor Price Table.")

# قسم رفع البيانات التاريخية
elif service == "Upload Historical Prices":
    st.subheader("Upload CSV/XLSX Historical Price Table")
    st.markdown("**Required Columns:** area, labor_hours, complexity, material_cost_per_unit, actual_cost")
    st.info("Upload with columns: area, labor_hours, complexity, material_cost_per_unit, actual_cost")

    st.markdown("### Required Project Info")
    hist_project_name = st.text_input("Project Name")
    hist_project_type = st.selectbox("Project Type", ["Substation", "OHTL", "Cables", "Civil", "Other"])
    hist_contractor = st.text_input("Contractor Name")
    hist_contract_value = st.number_input("Contract Value (SAR)", min_value=0.0)
    hist_year = st.number_input("Year of Execution", min_value=1990, max_value=2100)

    uploaded_file = st.file_uploader("Upload Historical Data", type=["csv", "xlsx"], key="historical_uploader")
    if uploaded_file:
        if all([hist_project_name, hist_project_type, hist_contractor, hist_contract_value, hist_year]):
            metadata = {
                "project_name": hist_project_name,
                "project_type": hist_project_type,
                "contractor": hist_contractor,
                "contract_value": hist_contract_value,
                "execution_year": hist_year
            }
            with st.spinner("Processing historical data..."):
                result = orch.archive_historical_prices(uploaded_file, metadata=metadata)
                st.success(result if "model trained" in result.lower() else result)
        else:
            st.warning("Please fill in all required project info before uploading.")
