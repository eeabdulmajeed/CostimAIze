
import openai
import streamlit as st

class CostimAIzeOrchestrator:
    def __init__(self):
        openai.api_key = st.secrets["OPENAI_API_KEY"]

    def detect_inquiries(self, sow_text):
        prompt = f"""
أنت مساعد هندسي ذكي. استلمت نطاق عمل لمشروع كهربائي. اقرأ النص التالي، وحدد فقط الاستفسارات الفنية أو المعلومات الناقصة التي قد تؤثر على تسعير المشروع. لا تشرح، فقط اكتب الاستفسارات:

"""{sow_text}"""

قائمة الاستفسارات:
- 
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    { "role": "user", "content": prompt }
                ],
                temperature=0.4
            )
            answer = response['choices'][0]['message']['content']
            inquiries = [line.strip("- ").strip() for line in answer.split("\n") if line.strip().startswith("-")]
            return inquiries

        except Exception as e:
            return [f"حدث خطأ أثناء تحليل الاستفسارات الذكية: {str(e)}"]

    def run_estimation(self, sow_text, historical_data):
        return {
            "مخرجات التقدير": "هنا توضع النتائج النهائية بعد المعالجة الذكية لاحقًا.",
            "نطاق العمل المدخل": sow_text[:300] + "..."  # للعرض فقط
        }
