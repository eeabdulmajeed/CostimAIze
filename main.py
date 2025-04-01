
import openai
import streamlit as st
import base64

st.set_page_config(page_title="CostimAIze | الذكاء الاصطناعي للتقدير والتحليل", layout="wide")
st.title("CostimAIze | التقدير والتحليل الذكي لمشاريع البنية التحتية")

# إدخال مدة تنفيذ المشروع
duration = st.slider("مدة تنفيذ المشروع (بالأشهر):", 6, 48, 24, step=6)

# رفع نطاق العمل
uploaded_file = st.file_uploader("ارفع ملف نطاق العمل (بصيغة .txt)")

# إدخال جدول أسعار المقاول (اختياري لتحليل العطاء)
st.markdown("---")
st.subheader("(اختياري) تحليل الأسعار المقدمة من المقاول")
price_table = st.text_area("الصق جدول الأسعار (بصيغة بند:سعر لكل بند)")

# زر لتنفيذ التحليل الكامل
if st.button("ابدأ التحليل الذكي"):
    if uploaded_file is not None:
        sow_text = uploaded_file.read().decode("utf-8")

        prompt = f"""You are a senior AI infrastructure cost analyst.

1. Forecast global market trends over the next {duration} months for:
- Copper
- Aluminum
- Steel
- Electrical equipment
- International shipping

2. Read and analyze the following Scope of Work (SOW) and extract:
- Key technical components
- Non-technical requirements (logistics, training, etc.)
- Any unclear or contradictory content
- Expected execution complexity
- List of components to be priced

3. Based on the extracted elements and expected market trends,
generate a full project cost estimate in Saudi Riyal (SAR).

4. If a price table is provided by a contractor, compare each line item with the estimated cost, and classify as:
- Acceptable (within reasonable range)
- High (above estimated by 15% or more)
- Missing (not covered)

Then summarize in a table.

Project duration: {duration} months

SOW:
{sow_text}

Price Table:
{price_table}
""" 

        try:
            client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a highly skilled infrastructure cost analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            result = response.choices[0].message.content

            st.subheader("نتائج التحليل والتقدير:")
            st.markdown(result)

            st.info(f"تم تضمين تأثير السوق المتوقع على مدى {duration} شهر ضمن التقدير.")
            st.warning("ملاحظة: صلاحية هذا التقدير 3 أشهر من تاريخ التحليل. يُوصى بإعادة التقدير في حال تأخر الطرح أو تغير السوق.")

            def create_download_link(text, filename):
                b64 = base64.b64encode(text.encode()).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">تحميل التقرير كنص</a>'
                return href

            st.markdown(create_download_link(result, "CostimAIze_Report.txt"), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بـ GPT: {e}")
    else:
        st.warning("الرجاء رفع ملف نطاق العمل قبل البدء.")
