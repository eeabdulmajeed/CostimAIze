
import streamlit as st
from costimaize_v8_main_full import CostimAIzeOrchestrator

st.title("CostimAIze - GPT Inquiry Engine")

api_key = st.text_input("Enter your OpenAI API Key (leave blank for local mode)", type="password")
uploaded_file = st.file_uploader("Upload SOW File", type=["txt"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")

    if api_key:
        st.info("Using GPT-4 for inquiry generation...")
    else:
        st.warning("No API key provided. Switching to local NLP engine.")

    estimator = CostimAIzeOrchestrator(api_key=api_key if api_key else None)
    inquiry_result = estimator.generate_inquiries(text)

    st.subheader(f"Inquiry Source: {inquiry_result['source']}")
    if isinstance(inquiry_result["questions"], str):
        st.text(inquiry_result["questions"])
    else:
        for q in inquiry_result["questions"]:
            st.markdown(f"- {q['text']}")
