
import openai
import streamlit as st
import textwrap

class CostimAIzeOrchestrator:
    def __init__(self):
        openai.api_key = st.secrets["OPENAI_API_KEY"]

    def detect_inquiries(self, sow_text):
        prompt = textwrap.dedent(f"""
            أنت مساعد هندسي ذكي. استلمت نطاق عمل لمشروع كهربائي.
            اقرأ النص التالي واستخرج الاستفسارات الفنية أو المعلومات الناقصة التي قد تؤثر على تسعير المشروع.

            لا تشرح. فقط اكتب الاستفسارات بصيغة نقاط واضحة ومنظمة:

            """{sow_text}"""

            قائمة الاستفسارات:
            -
        """)

        try:
            chat_completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            answer = chat_completion.choices[0].message.content
            inquiries = [line.strip("- ").strip() for line in answer.split("\n") if line.strip().startswith("-")]
            return inquiries if inquiries else ["لا توجد استفسارات واضحة."]
        except Exception as e:
            return [f"حدث خطأ أثناء تحليل الاستفسارات الذكية: {str(e)}"]

    def run_estimation(self, sow_text, historical_data):
        return {
            "ملخص التقدير": "هذا تقدير مبدئي بناءً على تحليل الذكاء الاصطناعي.",
            "مقتطف من نطاق العمل": sow_text[:300] + "..."
        }
