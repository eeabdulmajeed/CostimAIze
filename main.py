
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
        try:
            text = orch.extract_text(sow_file)
            st.session_state["sow_text"] = text
            st.session_state["is_valid"] = orch.validate_sow(text)
        except Exception as e:
            pass
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
            except Exception as e:
            pass
                st.json(result)

                import pandas as pd
                import io

                if "Breakdown" in result:
                    df = pd.DataFrame.from_dict(result["Breakdown"], orient="index", columns=["Estimated Cost"])
                    csv = df.to_csv().encode('utf-8')
                    st.download_button(
                        label="Download Estimate Breakdown (CSV)",
                        data=csv,
                        file_name="cost_estimate.csv",
                        mime="text/csv"
                    )


                import pandas as pd
                import io
                if "Breakdown" in result:
                    df = pd.DataFrame.from_dict(result["Breakdown"], orient="index", columns=["Estimated Price"])
                    buffer = io.StringIO()
                    df.to_csv(buffer)
                    st.download_button(
                        label="Download Cost Breakdown (CSV)",
                        data=buffer.getvalue(),
                        file_name="cost_estimation.csv",
                        mime="text/csv"
                    )


                import pandas as pd
                if isinstance(result, dict):
                    try:
                        df = pd.DataFrame([result])
                        st.download_button(
                            label="Download Estimation Result as CSV",
                            data=df.to_csv(index=False).encode('utf-8'),
                            file_name='estimation_result.csv',
                            mime='text/csv'
                    except Exception as e:
            pass
                        )
                    except Exception as e:
                        st.warning(f"Download failed: {str(e)}")


                import pandas as pd
                import io

                # تحميل نتائج التقدير
                if "Breakdown" in result:
                    df = pd.DataFrame(result["Breakdown"].items(), columns=["Component", "Estimated Cost"])
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download Estimation CSV", data=csv, file_name="estimation_result.csv", mime="text/csv")

                # تحميل تحليل الأسعار إن وُجد
                if "analysis" in result:
                    df_bid = pd.DataFrame(result["analysis"])
                    csv_bid = df_bid.to_csv(index=False).encode("utf-8")
                    st.download_button("Download Bid Analysis CSV", data=csv_bid, file_name="bid_analysis.csv", mime="text/csv")


                import pandas as pd
                import io
                est_result_df = pd.DataFrame.from_dict(result, orient='index').reset_index()
                est_result_df.columns = ['Metric', 'Value']
                csv = est_result_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Estimation Result as CSV", data=csv, file_name="estimation_result.csv", mime="text/csv")


                st.subheader("Smart AI Recommendations")
                if result.get("Used Historical Model") is False:
                    st.warning("لم يتم استخدام بيانات تاريخية - قد تكون النتائج أقل دقة.")
                if result.get("Model Confidence") and float(str(result["Model Confidence"]).replace('%','')) < 80:
                    st.warning("نموذج الذكاء غير واثق تمامًا من النتائج – ننصح بمراجعة البيانات التاريخية.")
                if result.get("Adjusted for Inquiry Gaps"):
                    st.warning(result["Adjusted for Inquiry Gaps"])

                
                st.subheader("AI Historical Data Analysis")
                st.markdown(f"**Used Historical Model:** {result.get('Used Historical Model', 'N/A')}")
                st.markdown(f"**Historical Data Size:** {result.get('Historical Data Size', 'N/A')}")
                st.markdown(f"**Model Confidence:** {result.get('Model Confidence', 'N/A')}")

        
                import pandas as pd
                if "Breakdown" in result:
                    breakdown_df = pd.DataFrame(result["Breakdown"].items(), columns=["Component", "Estimated Cost"])
                    st.download_button("Download Estimation Breakdown (CSV)", breakdown_df.to_csv(index=False).encode(), file_name="estimation_breakdown.csv", mime="text/csv")

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
    st.subheader("Bid Price Analysis")

    bid_sow = st.file_uploader("Upload Scope of Work for Bid", type=["pdf", "docx", "txt"], key="bid_sow")
    bid_table = st.file_uploader("Upload Contractor's Price Table (CSV)", type=["csv"], key="bid_prices")

    if bid_sow and bid_table:
        try:
            sow_text = orch.extract_text(bid_sow)
            import pandas as pd
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
        except Exception as e:
            pass
                    st.dataframe(pd.DataFrame(analysis["analysis"]))

                    if "analysis" in analysis:
                        df_result = pd.DataFrame(analysis["analysis"])
                        buffer = io.StringIO()
                        df_result.to_csv(buffer, index=False)
                        st.download_button(
                            label="Download Bid Analysis (CSV)",
                            data=buffer.getvalue(),
                            file_name="bid_analysis.csv",
                            mime="text/csv"
                        )

                    
                import pandas as pd
                df_result = pd.DataFrame(analysis["analysis"])
                st.download_button("Download Bid Analysis (CSV)", df_result.to_csv(index=False).encode(), file_name="bid_analysis.csv", mime="text/csv")


                if "analysis" in analysis:
                    bid_df = pd.DataFrame(analysis["analysis"])
                    bid_csv = bid_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Bid Analysis as CSV", data=bid_csv, file_name="bid_analysis.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Failed to analyze bid: {str(e)}")
    else:
        st.info("Please upload both SOW and Contractor Price Table.")
elif service == "Upload Historical Prices":
    
    uploaded_file = st.file_uploader("Upload Historical Data", type=["csv", "xlsx"])
    if uploaded_file:
        metadata = {
        "project_name": hist_project_name,
        "project_type": hist_project_type,
        "contractor": hist_contractor,
        "contract_value": hist_contract_value,
        "execution_year": hist_year
    }
    result = orch.archive_historical_prices(uploaded_file, metadata=metadata)
        st.success(result if "model trained" in result.lower() else result)
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