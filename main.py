import streamlit as st
import pandas as pd
import io
from costimaize_v8_main_full import CostimAIzeOrchestrator

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

orch = CostimAIzeOrchestrator()
service = st.selectbox("Select Service", ["Project Cost Estimation", "Bid Price Analysis", "Upload Historical Prices"])

if service == "Project Cost Estimation":
    st.subheader("Upload Scope of Work")
    sow_file = st.file_uploader("Upload SOW (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    if sow_file:
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
                st.markdown(f"- **{iq}**")
                response = st.text_input(f"Response to: {iq}", key=f"response_{i}")
                st.session_state["responses"][iq] = response

        p_type = st.selectbox("Project Type", ["Substation", "OHTL", "Cables", "Other"])
        location = st.text_input("Location")
        duration = st.text_input("Execution Duration (Months)")
        contract_type = st.selectbox("Contract Type", ["Lump Sum Turnkey", "Unit Rate", "LSTK & Unit Rate"])
        notes = st.text_area("Notes")

        if st.button("Run Smart Turnkey Estimation"):
            try:
                orch.set_context(p_type, location, duration, contract_type, notes, st.session_state["responses"])
                result = orch.run_estimation(st.session_state["sow_text"])
                st.session_state["result"] = result
                st.success("Estimation complete.")
                st.json(result)

                # تحميل تفاصيل التكلفة
                if "Breakdown" in result and isinstance(result["Breakdown"], dict):
                    breakdown_df = pd.DataFrame(result["Breakdown"].items(), columns=["Component", "Estimated Cost"])
                    st.download_button(
                        label="Download Estimation Breakdown (CSV)",
                        data=breakdown_df.to_csv(index=False).encode('utf-8'),
                        file_name="estimation_breakdown.csv",
                        mime="text/csv"
                    )

                # تحميل النتيجة الكاملة
                est_result_df = pd.DataFrame.from_dict(result, orient='index').reset_index()
                est_result_df.columns = ['Metric', 'Value']
                st.download_button(
                    label="Download Estimation Result (CSV)",
                    data=est_result_df.to_csv(index=False).encode('utf-8'),
                    file_name="estimation_result.csv",
                    mime="text/csv"
                )

                # توصيات الذكاء الاصطناعي
                st.subheader("Smart AI Recommendations")
                if "Used Historical Model" in result and not result["Used Historical Model"]:
                    st.warning("لم يتم استخدام بيانات تاريخية - قد تكون النتائج أقل دقة.")
                if "Model Confidence" in result and float(str(result["Model Confidence"]).replace('%', '')) < 80:
                    st.warning("نموذج الذكاء غير واثق تمامًا من النتائج – ننصح بمراجعة البيانات التاريخية.")
                if "Adjusted for Inquiry Gaps" in result:
                    st.warning(result["Adjusted for Inquiry Gaps"])

                # تحليل البيانات التاريخية
                st.subheader("AI Historical Data Analysis")
                st.markdown(f"**Used Historical Model:** {result.get('Used Historical Model', 'N/A')}")
                st.markdown(f"**Historical Data Size:** {result.get('Historical Data Size', 'N/A')}")
                st.markdown(f"**Model Confidence:** {result.get('Model Confidence', 'N/A')}")

                # تحليل الكلمات المفتاحية والنتائج الفنية
                st.subheader("Keyword Analysis")
                st.write(result.get("Keyword Analysis", {}))
                st.subheader("Technical Findings")
                st.write(result.get("Inquiries", []))

            except Exception as e:
                st.error(f"Estimation failed: {str(e)}")

    elif "sow_text" in st.session_state and not st.session_state.get("is_valid"):
        st.error("The uploaded file does not meet minimum project scope requirements.")
        st.write("Keyword Analysis:", st.session_state.get("keyword_analysis", {}))

elif service == "Bid Price Analysis":
    st.subheader("Bid Price Analysis (Under Development)")
    bid_sow = st.file_uploader("Upload Scope of Work for Bid", type=["pdf", "docx", "txt"], key="bid_sow")
    bid_table = st.file_uploader("Upload Contractor's Price Table (CSV)", type=["csv"], key="bid_prices")

    if bid_sow and bid_table:
        try:
            sow_text = orch.extract_text(bid_sow)
            df = pd.read_csv(bid_table)
            required = {"description", "quantity", "unit_price"}
            if not required.issubset(df.columns):
                st.error("CSV must include: description, quantity, unit_price")
            else:
                contractor_data = df.to_dict(orient='records')
                st.warning("Bid analysis feature is not yet implemented.")
        except Exception as e:
            st.error(f"Failed to analyze bid: {str(e)}")
    else:
        st.info("Please upload both SOW and Contractor Price Table.")

elif service == "Upload Historical Prices":
    st.subheader("Upload CSV/XLSX Historical Price Table")
    st.info("Upload with columns: area, labor_hours, complexity, material_cost_per_unit, actual_cost")

    st.markdown("### Required Project Info")
    hist_project_name = st.text_input("Project Name")
    hist_project_type = st.selectbox("Project Type", ["Substation", "OHTL", "Cables", "Civil", "Other"])
    hist_contractor = st.text_input("Contractor Name")
    hist_contract_value = st.text_input("Contract Value (SAR)")
    hist_year = st.text_input("Year of Execution")

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
            result = orch.archive_historical_prices(uploaded_file, metadata=metadata)
            st.success(result if "model trained" in result.lower() else result)
        else:
            st.warning("Please fill in all required project info before uploading.")