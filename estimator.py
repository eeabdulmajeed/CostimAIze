import openai
import os
import time
from constants import PRUDENTAI_DEFAULT_CONFIDENCE, EXAMPLE_RISK_FACTORS, HISTORICAL_REVIEW_NOTE

# تأكد من أن مفتاح GPT مضاف إلى بيئة النظام أو داخل Streamlit Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")


def run_prudent_estimator(sow_file):
    """
    الذكاء الفعلي لسيناريو PrudentAI
    يحلل نطاق العمل ويُنتج سعر تقديري مع مبررات واضحة
    """
    # اقرأ النص من ملف نطاق العمل (بشكل مبسط حالياً)
    sow_text = sow_file.read().decode("utf-8", errors="ignore")

    prompt = f"""
    أنت مهندس تسعير ذكي. أمامك نطاق عمل لمشروع. قم بتقدير تكلفة تنفيذ هذا المشروع كنظام تسليم مفتاح.

    نطاق العمل:
    {sow_text}

    المطلوب:
    - تقدير تكلفة إجمالية معقولة (بالريال)
    - توضيح عوامل الخطر أو الحذر (إن وجدت)
    - درجة الثقة (مرتفعة / متوسطة / منخفضة)
    - شرح منطقي مختصر لقرار التسعير

    النتيجة المطلوبة بصيغة JSON فقط دون شرح إضافي:
    {{
      "السعر التقديري": "... ريال",
      "درجة الثقة": "...",
      "عوامل الحذر": ["..."],
      "شرح القرار": "..."
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        result = response.choices[0].message.content
        return eval(result)
    
    except Exception as e:
        return {
            "السعر التقديري": "تعذر التقدير",
            "درجة الثقة": PRUDENTAI_DEFAULT_CONFIDENCE,
            "عوامل الحذر": EXAMPLE_RISK_FACTORS,
            "شرح القرار": f"حدث خطأ أثناء تنفيذ الذكاء: {e}"
        }

