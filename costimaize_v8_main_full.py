
import openai
import streamlit as st

class CostimAIzeOrchestrator:
    def __init__(self):
        openai.api_key = st.secrets["OPENAI_API_KEY"]

    def detect_inquiries(self, sow_text):
        prompt = f'''
أنت مساعد هندسي ذكي. استلمت نطاق عمل لمشروع كهربائي. اقرأ النص التالي، وحدد فقط الاستفسارات الفنية أو المعلومات الناقصة التي قد تؤثر على تسعير المشروع. لا تشرح، فقط اكتب الاستفسارات:

"""{sow_text}"""

قائمة الاستفسارات:
- 
'''

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
            return inquiries if inquiries else ["لم يتم العثور على استفسارات واضحة."]
        except Exception as e:
            return [f"حدث خطأ أثناء تحليل الاستفسارات: {str(e)}"]

    def run_estimation(self, sow_text, historical_data):
        # نموذج مبسط لعرض النتائج
        return {
            "ملخص التقدير": "هذا ملخص أولي للتكلفة المقدرة باستخدام الذكاء الاصطناعي.",
            "أبرز الملاحظات": [
                "التحليل يعتمد على الفهم الذكي لنطاق العمل.",
                "يمكن تطوير النتائج بربط النظام بأسعار فعلية لاحقًا."
            ],
            "مقتطف من نطاق العمل": sow_text[:300] + "..."
        }
