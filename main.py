import streamlit as st
import openai
import json
import os
from typing import Dict, Optional
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from docx import Document
import PyPDF2

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.proxies = None  # تعطيل أي إعدادات proxies

# اختبار OpenAI API
try:
    test_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, can you respond?"}],
        max_tokens=10
    )
    print("OpenAI API test successful:", test_response.choices[0].message.content)
except Exception as e:
    print("OpenAI API test failed:", str(e))

# Helper function to fetch market data
def fetch_helper_data() -> Dict:
    """Fetch real market data (simulated for now)."""
    try:
        return {
            "inflation_rate": 1.06,  # 6% تضخم (محاكاة)
            "material_cost": 700,    # دولار لكل وحدة (محاكاة)
            "labor_rate": 350,       # دولار/ساعة (محاكاة)
            "global_news": "Stable economic conditions globally."
        }
    except Exception as e:
        print(f"Error fetching real market data: {e}")
        return {
            "inflation_rate": 1.03,
            "material_cost": 500,
            "labor_rate": 250,
            "global_news": "غير قادر على جلب الأخبار العالمية."
        }

# Cost estimation class with cautious pricing logic using OpenAI
class CostEstimator:
    def __init__(self):
        # Dictionary to store historical prices for 90 days
        if "price_history" not in st.session_state:
            st.session_state.price_history = {}
        self.price_history = st.session_state.price_history

        # Lists to store projects and bids in session state
        if "projects" not in st.session_state:
            st.session_state.projects = []
        if "bids" not in st.session_state:
            st.session_state.bids = []

    def read_file(self, uploaded_file) -> str:
        """Read content from uploaded files (Word, Excel, PDF)."""
        content = ""
        print(f"Attempting to read file: {uploaded_file.name}")
        try:
            if uploaded_file.name.endswith(".docx"):
                doc = Document(uploaded_file)
                content = "\n".join([para.text for para in doc.paragraphs])
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                content = df.to_string()
            elif uploaded_file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(uploaded_file)
                content = "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            st.error(f"فشل في قراءة الملف {uploaded_file.name}: {str(e)}")
            print(f"Error reading file {uploaded_file.name}: {str(e)}")
        print(f"File content for {uploaded_file.name}: {content}")
        if not content.strip():
            st.warning(f"لم يتم استخراج أي محتوى من الملف {uploaded_file.name}. يرجى التأكد من أن الملف ليس فارغًا أو تالفًا.")
        return content

    def validate_scope(self, task_description: str) -> Dict:
        """Analyze the scope of work for contradictions and extract main tasks using OpenAI."""
        if not task_description.strip():
            return {"tasks": [], "contradictions": ["لم يتم العثور على محتوى في الملف المرفوع"]}
        
        print(f"Sending task description to OpenAI: {task_description}")
        prompt = f"""
        As a cautious pricing engineer, analyze the following scope of work to extract ALL main tasks and detect any contradictions. Main tasks include all activities required to complete the project, such as (but not limited to) material procurement, labor, installation, testing, and commissioning. Contradictions may include inconsistencies in the scope, timeline, or requirements. Return the result in JSON format with fields:
        - tasks: list of all identified tasks
        - contradictions: list of contradictions if any
        Text: {task_description}
        """
        try:
            with st.spinner("جارٍ تحليل نطاق العمل..."):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cautious pricing engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.5
                )
            if not response.choices or not response.choices[0].message.content:
                return {"tasks": [], "contradictions": ["لم يتم تلقي استجابة من OpenAI"]}
            response_content = response.choices[0].message.content.strip()
            print(f"OpenAI response content: {response_content}")
            if not response_content:
                return {"tasks": [], "contradictions": ["استجابة فارغة من OpenAI"]}
            if response_content.startswith("...json"):
                response_content = response_content[7:].strip()
            if not response_content.startswith("{"):
                return {"tasks": [], "contradictions": [f"تنسيق JSON غير صالح من OpenAI: {response_content}"]}
            return json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return {"tasks": [], "contradictions": [f"استجابة JSON غير صالحة من OpenAI: {response_content}"]}
        except Exception as e:
            print(f"Error in validate_scope: {str(e)}")
            return {"tasks": [], "contradictions": [f"فشل في تحليل نطاق العمل: {str(e)}"]}

    def estimate_cost_once(self, task_description: str, helper_data: Dict) -> Dict:
        """Run a single cost estimation using OpenAI."""
        prompt = f"""
        As a cautious pricing engineer, estimate the cost for the following scope of work. You must identify and analyze ALL direct costs (including but not limited to materials, labor, installation, testing, commissioning) and ALL indirect costs (including but not limited to safety, security, shipping, financing) relevant to the scope of work. The examples provided are illustrative only, and you should consider any additional direct or indirect costs that may apply based on the project details. For each item, provide a unit cost (e.g., per square meter, per hour) and the total cost based on your analysis of global and local market conditions, including inflation, labor rates, material availability, and demand fluctuations. Consider the project's location as specified in the scope of work (if provided) and account for relevant local market conditions (e.g., labor rates, material availability, construction regulations) alongside global market conditions (e.g., inflation, demand fluctuations). If the location is not specified, use your best judgment to estimate costs based on typical market conditions for the region or context implied by the scope of work. Provide a detailed cost breakdown and explain how you arrived at each figure, ensuring logical consistency and avoiding random guesses.

        Scope of Work: {task_description}

        Return the result in JSON format with:
        - total_cost: the total estimated cost in USD
        - cost_breakdown: a detailed breakdown of the cost into direct and indirect components with unit costs
        - reasoning: a detailed explanation of how you determined each cost component
        """
        try:
            with st.spinner("جارٍ تقدير التكلفة..."):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cautious pricing engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Error in estimate_cost_once: {e}")
            return None

    def cautious_pricing(self, costs: list, historical_costs: list, task_description: str, helper_data: Dict) -> Dict:
        """Apply cautious pricing logic using OpenAI to ensure logical pricing."""
        if not costs:
            return {"error": "لم يتم الحصول على تقديرات تكلفة صالحة من المحاكاة"}

        # Prepare historical costs for OpenAI
        historical_costs_str = ", ".join([str(cost) for cost in historical_costs]) if historical_costs else "لا توجد تكاليف تاريخية متاحة"

        prompt = f"""
        As a cautious pricing engineer, you have run 100 cost estimation simulations for the following task: {task_description}. The estimated costs are: {costs}. Historical costs for similar tasks are: {historical_costs_str}. Helper data available: inflation_rate={helper_data['inflation_rate']}, material_cost={helper_data['material_cost']}, labor_rate={helper_data['labor_rate']}, global_news={helper_data['global_news']}. Your task is to:
        1. Determine the final cost estimate, ensuring it is logical and avoids hallucination or randomness.
        2. Consider the scope of work, project conditions, global market conditions (e.g., inflation, demand fluctuations), and historical costs (if relevant).
        3. Consider the project's location as specified in the scope of work (if provided) and account for relevant local market conditions (e.g., labor rates, material availability, construction regulations) alongside global market conditions. If the location is not specified, use your best judgment to estimate costs based on typical market conditions for the region or context implied by the scope of work.
        4. Break down the final cost into ALL direct costs (including but not limited to materials, labor, installation, testing, commissioning) and ALL indirect costs (including but not limited to safety, security, shipping, financing) relevant to the scope of work, with unit costs for each item where applicable.
        5. Explain each component in detail, ensuring logical consistency.
        Return the result in JSON format with:
        - final_cost: the final cost estimate in USD
        - cost_breakdown: a detailed breakdown of the cost into direct and indirect components with unit costs
        - reasoning: a detailed explanation of how you determined the final cost, including any adjustments for logical consistency
        """
        try:
            with st.spinner("جارٍ تطبيق منطق التسعير الحذر..."):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cautious pricing engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
            result = json.loads(response.choices[0].message.content.strip())
            return {
                "final_cost": result["final_cost"],
                "cost_breakdown": result.get("cost_breakdown", {}),
                "reasoning": result["reasoning"]
            }
        except Exception as e:
            print(f"Error in cautious_pricing: {e}")
            return {"error": "فشل في تطبيق منطق التسعير الحذر"}

    def analyze_and_estimate(self, task_description: str) -> Dict:
        """Estimate cost with cautious pricing logic and Monte Carlo simulation."""
        # Check if the task has a recent estimate (within 90 days)
        if task_description in self.price_history:
            entry = self.price_history[task_description]
            timestamp = entry["timestamp"]
            current_time = datetime.now().timestamp()
            if current_time - timestamp < 90 * 24 * 60 * 60:  # 90 days in seconds
                return {
                    "tasks": entry.get("tasks", []),
                    "contradictions": entry.get("contradictions", []),
                    "total_cost": entry["cost"],
                    "cost_breakdown": entry.get("cost_breakdown", {}),
                    "reasoning": "تم استرجاع التقدير من البيانات التاريخية (خلال 90 يومًا)."
                }

        # Validate scope of work
        scope_analysis = self.validate_scope(task_description)
        contradictions = scope_analysis["contradictions"]
        tasks = scope_analysis["tasks"]

        # If contradictions exist, return them for user clarification
        if contradictions:
            return {
                "tasks": tasks,
                "contradictions": contradictions,
                "total_cost": None,
                "cost_breakdown": {},
                "reasoning": "تم اكتشاف تناقضات، يرجى حلها قبل تقدير التكلفة."
            }

        # Fetch market data
        helper_data = fetch_helper_data()

        # Monte Carlo simulation: Run 100 simulations
        costs = []
        reasonings = []
        cost_breakdowns = []
        for i in range(100):
            st.info(f"جارٍ تشغيل المحاكاة {i+1} من 100...")
            result = self.estimate_cost_once(task_description, helper_data)
            if result is not None and "total_cost" in result:
                costs.append(result["total_cost"])
                reasonings.append(result["reasoning"])
                cost_breakdowns.append(result.get("cost_breakdown", {}))

        # Get historical costs for comparison
        historical_costs = [entry["cost"] for entry in self.price_history.values()]

        # Apply cautious pricing logic using OpenAI
        cautious_result = self.cautious_pricing(costs, historical_costs, task_description, helper_data)
        if "error" in cautious_result:
            return {"error": cautious_result["error"]}

        final_cost = cautious_result["final_cost"]
        cost_breakdown = cautious_result["cost_breakdown"]
        reasoning = cautious_result["reasoning"]

        # Store the result in price history and session state
        result = {
            "tasks": tasks,
            "contradictions": contradictions,
            "total_cost": final_cost,
            "cost_breakdown": cost_breakdown,
            "reasoning": reasoning
        }
        self.price_history[task_description] = {
            "cost": final_cost,
            "cost_breakdown": cost_breakdown,
            "tasks": tasks,
            "contradictions": contradictions,
            "timestamp": datetime.now().timestamp()
        }
        st.session_state.price_history = self.price_history

        # Save to session state
        st.session_state.projects.append({
            "task_description": task_description,
            "total_cost": final_cost,
            "timestamp": datetime.now().timestamp()
        })

        return result

    def compare_with_bid(self, task_description: str, actual_bid: float) -> Dict:
        prompt = f"""
        As a cautious pricing engineer, compare the actual bid with the previous estimate based on the text: {task_description}. Actual bid: {actual_bid} USD. Return the result in JSON format with fields:
        - estimated_cost: estimated cost
        - actual_bid: actual bid
        - deviation_percent: deviation percentage
        - recommendation: recommendation for adjustment if needed
        """
        try:
            with st.spinner("جارٍ تحليل العطاء..."):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cautious pricing engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.5
                )
            result = json.loads(response.choices[0].message.content.strip())
            # Save to session state
            st.session_state.bids.append({
                "task_description": task_description,
                "actual_bid": actual_bid,
                "timestamp": datetime.now().timestamp()
            })
            return result
        except Exception as e:
            print(f"Error in compare_with_bid: {e}")
            return {"error": "فشل في تحليل العطاء"}

    def update_with_user_input(self, task_description: str, user_input: str) -> Dict:
        prompt = f"""
        As a cautious pricing engineer, update the previous estimate for the text: {task_description} based on the comments: {user_input}. Return the result in JSON format with fields:
        - updated_cost: updated cost
        - reasoning: explanation of the adjustment
        """
        try:
            with st.spinner("جارٍ تحديث التقدير بناءً على المدخلات..."):
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cautious pricing engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.6
                )
            return json.loads(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"Error in update_with_user_input: {e}")
            return {"error": "فشل في تحديث التقدير"}

# Dashboard statistics from session state
def get_dashboard_stats():
    total_projects = len(st.session_state.get("projects", []))
    total_cost_estimated = sum(project["total_cost"] for project in st.session_state.get("projects", []))
    bids_analyzed = len(st.session_state.get("bids", []))
    historical_prices_archived = len(st.session_state.get("price_history", {}))
    return {
        "total_projects": total_projects,
        "total_cost_estimated": total_cost_estimated,
        "bids_analyzed": bids_analyzed,
        "historical_prices_archived": historical_prices_archived
    }

# Streamlit app with dashboard and service selection
st.title("CostimAIze - Smart Pricing Engineer")
st.image("assets/logo.png", use_column_width=True)

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    if st.button("Dashboard"):
        st.session_state.page = "dashboard"
    if st.button("Estimate Cost"):
        st.session_state.page = "estimate_cost"
    if st.button("Analyze Bids"):
        st.session_state.page = "analyze_bids"
    if st.button("Archive Historical Prices"):
        st.session_state.page = "archive_prices"

# Dashboard page
if st.session_state.page == "dashboard":
    st.header("Dashboard")
    stats = get_dashboard_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", stats["total_projects"])
    with col2:
        st.metric("Total Cost Estimated (USD)", stats["total_cost_estimated"])
    with col3:
        st.metric("Bids Analyzed", stats["bids_analyzed"])
    with col4:
        st.metric("Historical Prices Archived", stats["historical_prices_archived"])

    st.subheader("Our Services")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Estimate Cost", key="dashboard_estimate"):
            st.session_state.page = "estimate_cost"
    with col2:
        if st.button("Analyze Bids", key="dashboard_analyze"):
            st.session_state.page = "analyze_bids"
    with col3:
        if st.button("Archive Historical Prices", key="dashboard_archive"):
            st.session_state.page = "archive_prices"

# Estimate Cost page
elif st.session_state.page == "estimate_cost":
    st.header("Estimate Cost")
    
    # File upload for scope of work
    uploaded_files = st.file_uploader("Upload Scope of Work (Word, Excel, PDF)", type=["docx", "xlsx", "pdf"], accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success("Files uploaded successfully!")

    # Analyze scope of work and show contradictions
    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        st.subheader("Scope Analysis")
        estimator = CostEstimator()
        contradictions = []
        task_description = ""
        for uploaded_file in st.session_state.uploaded_files:
            content = estimator.read_file(uploaded_file)
            task_description += f"File: {uploaded_file.name}\n{content}\n"
            with st.spinner("جارٍ تحليل نطاق العمل..."):
                scope_analysis = estimator.validate_scope(content)
                contradictions.extend(scope_analysis["contradictions"])
                st.session_state.tasks = scope_analysis["tasks"]

        st.session_state.task_description = task_description

        # Display contradictions and allow user input
        if contradictions:
            st.subheader("Contradictions Found")
            for i, contradiction in enumerate(contradictions):
                st.write(f"Contradiction {i+1}: {contradiction}")
                user_response = st.text_input(f"Response to contradiction {i+1}:", key=f"contradiction_{i}")
                if user_response:
                    st.session_state[f"contradiction_response_{i}"] = user_response
        elif not st.session_state.tasks:
            st.warning("لم تظهر أي نتائج. يرجى المحاولة مرة أخرى أو التحقق من السجلات لمعرفة الأخطاء.")
        else:
            st.subheader("Extracted Tasks")
            for i, task in enumerate(st.session_state.tasks):
                st.write(f"Task {i+1}: {task}")

        # Estimate cost after resolving contradictions
        if st.button("Proceed to Estimate Cost"):
            final_description = st.session_state.task_description
            if "contradiction_response_0" in st.session_state:
                final_description += f" with user responses: {st.session_state['contradiction_response_0']}"
            with st.spinner("جارٍ تقدير التكلفة..."):
                result = estimator.analyze_and_estimate(final_description)
            st.session_state.estimation_result = result
            st.session_state.page = "estimation_result"

# Estimation Result page
elif st.session_state.page == "estimation_result":
    st.header("Cost Estimation Report")
    if "estimation_result" in st.session_state:
        result = st.session_state.estimation_result
        if "error" in result:
            st.error(result["error"])
        else:
            st.subheader("Extracted Tasks")
            for i, task in enumerate(result["tasks"]):
                st.write(f"Task {i+1}: {task}")
            st.subheader("Contradictions")
            if result["contradictions"]:
                for i, contradiction in enumerate(result["contradictions"]):
                    st.write(f"Contradiction {i+1}: {contradiction}")
            else:
                st.write("No contradictions found.")
            st.subheader("Cost Estimation")
            st.write("Total Cost (USD):", result["total_cost"])
            st.subheader("Cost Breakdown")
            if result["cost_breakdown"]:
                st.subheader("Direct Costs")
                if "direct_costs" in result["cost_breakdown"]:
                    for component, details in result["cost_breakdown"]["direct_costs"].items():
                        if isinstance(details, dict) and "total" in details:
                            st.write(f"{component}: {details['total']} USD (Unit Cost: {details.get('unit_cost', 'N/A')}, Quantity: {details.get('quantity', 'N/A')})")
                        else:
                            st.write(f"{component}: {details} USD")
                st.subheader("Indirect Costs")
                if "indirect_costs" in result["cost_breakdown"]:
                    for component, details in result["cost_breakdown"]["indirect_costs"].items():
                        if isinstance(details, dict) and "total" in details:
                            st.write(f"{component}: {details['total']} USD (Unit Cost: {details.get('unit_cost', 'N/A')}, Quantity: {details.get('quantity', 'N/A')})")
                        else:
                            st.write(f"{component}: {details} USD")
            else:
                st.write("No cost breakdown available.")
            st.subheader("Reasoning")
            st.write(result["reasoning"])
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"

# Analyze Bids page
elif st.session_state.page == "analyze_bids":
    st.header("Analyze Bids")
    task_description = st.text_area("Enter task description for bid analysis:", "Build a small house with 3 rooms in a high-inflation area")
    actual_bid = st.number_input("Enter actual bid (USD):", min_value=0.0)
    if st.button("Analyze Bid"):
        estimator = CostEstimator()
        with st.spinner("جارٍ تحليل العطاء..."):
            analysis = estimator.compare_with_bid(task_description, actual_bid)
        if "error" in analysis:
            st.error(analysis["error"])
        else:
            st.write("Estimated Cost (USD):", analysis["estimated_cost"])
            st.write("Actual Bid (USD):", analysis["actual_bid"])
            st.write("Deviation (%):", analysis["deviation_percent"])
            st.write("Recommendation:", analysis["recommendation"])
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"

# Archive Historical Prices page
elif st.session_state.page == "archive_prices":
    st.header("Archive Historical Prices")
    st.write("Historical prices are archived for 90 days.")
    estimator = CostEstimator()
    if estimator.price_history:
        for task, data in estimator.price_history.items():
            st.write(f"Task: {task}, Cost: {data['cost']} USD, Timestamp: {datetime.fromtimestamp(data['timestamp'])}")
    else:
        st.write("No historical prices available.")
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"