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
        model="gpt-4-turbo",
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
        if "price_history" not in st.session_state:
            st.session_state.price_history = {}
        self.price_history = st.session_state.price_history

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
        """Analyze the scope of work for contradictions and extract main tasks using OpenAI (ScopeGPT)."""
        if not task_description.strip():
            return {"tasks": [], "contradictions": ["لم يتم العثور على محتوى في الملف المرفوع"], "missing_details": []}
        
        print(f"Sending task description to OpenAI (ScopeGPT): {task_description}")
        prompt = f"""
        You are ScopeGPT, a cautious pricing engineer specialized in scope analysis. Analyze the following scope of work to extract ALL main tasks and detect any contradictions. Main tasks include all activities required to complete the project, such as (but not limited to) material procurement, labor, installation, testing, commissioning, cybersecurity measures, and training programs. Contradictions may include inconsistencies in the scope, timeline, or requirements (e.g., conflicting timelines, missing critical details like location or material specifications, or tasks that do not align logically). If critical details are missing (e.g., timeline, location, or material specifications), note them as potential issues but do not consider them contradictions unless they directly conflict with other parts of the scope. Return the result in JSON format with fields:
        - tasks: list of all identified tasks
        - contradictions: list of contradictions if any (or an empty list if none are found)
        - missing_details: list of missing details that may affect cost estimation but are not contradictions
        Text: {task_description}
        """
        try:
            with st.spinner("جارٍ تحليل نطاق العمل..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are ScopeGPT, a cautious pricing engineer specialized in scope analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.5
                )
            if not response.choices or not response.choices[0].message.content:
                return {"tasks": [], "contradictions": ["لم يتم تلقي استجابة من OpenAI"], "missing_details": []}
            response_content = response.choices[0].message.content.strip()
            print(f"OpenAI response content (ScopeGPT): {response_content}")
            if not response_content:
                return {"tasks": [], "contradictions": ["استجابة فارغة من OpenAI"], "missing_details": []}
            if response_content.startswith("...json"):
                response_content = response_content[7:].strip()
            if not response_content.startswith("{"):
                return {"tasks": [], "contradictions": [f"تنسيق JSON غير صالح من OpenAI: {response_content}"], "missing_details": []}
            return json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return {"tasks": [], "contradictions": [f"استجابة JSON غير صالحة من OpenAI: {response_content}"], "missing_details": []}
        except Exception as e:
            print(f"Error in validate_scope: {str(e)}")
            return {"tasks": [], "contradictions": [f"فشل في تحليل نطاق العمل: {str(e)}"], "missing_details": []}

    def estimate_cost_once(self, task_description: str, helper_data: Dict) -> Dict:
        """Run a single cost estimation using OpenAI (MarketGPT)."""
        prompt = f"""
        You are MarketGPT, a cautious pricing engineer specialized in cost estimation. Estimate the cost for the following scope of work. You must identify and analyze ALL direct costs (including but not limited to materials, labor, installation, testing, commissioning) and ALL indirect costs (including but not limited to safety, security, shipping, financing) relevant to the scope of work. For each item, provide a unit cost (e.g., per square meter, per hour) and the total cost based on your analysis of global and local market conditions, including inflation, labor rates, material availability, and demand fluctuations. Consider the project's location as specified in the scope of work (if provided) and account for relevant local market conditions (e.g., labor rates, material availability, construction regulations) alongside global market conditions (e.g., inflation, demand fluctuations). If the location is not specified, use your best judgment to estimate costs based on typical market conditions for the region or context implied by the scope of work. Provide a detailed cost breakdown and explain how you arrived at each figure, ensuring logical consistency and avoiding random guesses.

        Scope of Work: {task_description}

        Return the result in JSON format with:
        - total_cost: the total estimated cost in USD
        - cost_breakdown: a detailed breakdown of the cost into direct and indirect components with unit costs
        - reasoning: a detailed explanation of how you determined each cost component
        """
        try:
            with st.spinner("جارٍ تقدير التكلفة..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are MarketGPT, a cautious pricing engineer specialized in cost estimation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7,
                    timeout=30
                )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Error in estimate_cost_once: {e}")
            return None

    def validate_cost(self, costs: list, historical_costs: list, task_description: str, helper_data: Dict) -> Dict:
        """Validate the estimated costs using OpenAI (ValidatorGPT)."""
        if not costs:
            return {"error": "لم يتم الحصول على تقديرات تكلفة صالحة من المحاكاة"}

        historical_costs_str = ", ".join([str(cost) for cost in historical_costs]) if historical_costs else "لا توجد تكاليف تاريخية متاحة"

        prompt = f"""
        You are ValidatorGPT, a cautious pricing engineer specialized in validating cost estimates. You have run 10 cost estimation simulations for the following task: {task_description}. The estimated costs are: {costs}. Historical costs for similar tasks are: {historical_costs_str}. Helper data available: inflation_rate={helper_data['inflation_rate']}, material_cost={helper_data['material_cost']}, labor_rate={helper_data['labor_rate']}, global_news={helper_data['global_news']}. Your task is to:
        1. Validate the estimated costs for logical consistency, ensuring they are neither too high nor too low compared to historical data and market conditions.
        2. Consider the scope of work, project conditions, global market conditions (e.g., inflation, demand fluctuations), and historical costs (if relevant).
        3. Consider the project's location as specified in the scope of work (if provided) and account for relevant local market conditions (e.g., labor rates, material availability, construction regulations) alongside global market conditions. If the location is not specified, use your best judgment to estimate costs based on typical market conditions for the region or context implied by the scope of work.
        4. Identify any discrepancies in the cost estimates (e.g., too high, too low, inconsistent with market conditions, timeline issues).
        5. If a discrepancy is found, explain the issue in detail and request clarification on: direct costs (materials, labor, equipment), indirect costs (shipping, safety, management), market factors (inflation, material costs, labor rates), and timeline impact.
        Return the result in JSON format with:
        - is_valid: boolean indicating if the cost is logically consistent
        - discrepancy: description of any discrepancy found (or "No discrepancy" if none)
        - clarification_request: detailed request for clarification if a discrepancy is found (or empty string if none)
        """
        try:
            with st.spinner("جارٍ التحقق من منطقية التكلفة..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are ValidatorGPT, a cautious pricing engineer specialized in validating cost estimates."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7,
                    timeout=30
                )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Error in validate_cost: {e}")
            return {"error": "فشل في التحقق من منطقية التكلفة"}

    def request_clarification(self, task_description: str, helper_data: Dict, clarification_request: str) -> Dict:
        """Request clarification from MarketGPT using OpenAI."""
        prompt = f"""
        You are MarketGPT, a cautious pricing engineer specialized in cost estimation. ValidatorGPT has requested clarification on the following cost estimate for the scope of work: {task_description}. Helper data available: inflation_rate={helper_data['inflation_rate']}, material_cost={helper_data['material_cost']}, labor_rate={helper_data['labor_rate']}, global_news={helper_data['global_news']}. The clarification request is: {clarification_request}. Provide a detailed explanation addressing the request, including:
        - Itemized breakdown of direct costs (materials, labor, equipment) with specific values.
        - Itemized breakdown of indirect costs (shipping, safety, management) with specific values.
        - Specific market factors (inflation rate, material cost changes, labor rate changes) with values.
        - Impact of the timeline on the cost (e.g., need for additional labor, expedited shipping).
        Return the result in JSON format with:
        - total_cost: the revised total estimated cost in USD (if applicable)
        - cost_breakdown: a detailed breakdown of the cost into direct and indirect components with unit costs
        - reasoning: a detailed explanation addressing the clarification request
        """
        try:
            with st.spinner("جارٍ طلب توضيح من MarketGPT..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are MarketGPT, a cautious pricing engineer specialized in cost estimation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7,
                    timeout=30
                )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Error in request_clarification: {e}")
            return {"error": "فشل في طلب التوضيح من MarketGPT"}

    def compare_with_bid(self, task_description: str, actual_bid: float) -> Dict:
        """Compare the estimated cost with the actual bid using OpenAI (BidGPT)."""
        prompt = f"""
        You are BidGPT, a cautious pricing engineer specialized in bid analysis. Compare the actual bid with the previous estimate based on the text: {task_description}. Actual bid: {actual_bid} USD. Return the result in JSON format with fields:
        - estimated_cost: estimated cost
        - actual_bid: actual bid
        - deviation_percent: deviation percentage
        - recommendation: recommendation for adjustment if needed
        """
        try:
            with st.spinner("جارٍ تحليل العطاء..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are BidGPT, a cautious pricing engineer specialized in bid analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.5,
                    timeout=30
                )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Error in compare_with_bid: {e}")
            return {"error": "فشل في تحليل العطاء"}

    def update_with_user_input(self, task_description: str, user_input: str) -> Dict:
        """Update the previous estimate based on user input using OpenAI."""
        prompt = f"""
        You are a cautious pricing engineer. Update the previous estimate for the text: {task_description} based on the comments: {user_input}. Return the result in JSON format with fields:
        - updated_cost: updated cost
        - reasoning: explanation of the adjustment
        """
        try:
            with st.spinner("جارٍ تحديث التقدير بناءً على المدخلات..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a cautious pricing engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.6,
                    timeout=30
                )
            return json.loads(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"Error in update_with_user_input: {e}")
            return {"error": "فشل في تحديث التقدير"}

    def coordinate_results(self, task_description: str, scope_result: Dict, market_result: Dict, validator_result: Dict, bid_result: Dict, dialogue_log: Dict) -> Dict:
        """Coordinate the results from all agents using OpenAI (CoordinatorGPT)."""
        prompt = f"""
        You are CoordinatorGPT, a cautious pricing engineer tasked with coordinating results from multiple agents and making a final decision. Here are the results from the agents for the scope of work: {task_description}:
        - ScopeGPT: {scope_result}
        - MarketGPT: {market_result}
        - ValidatorGPT: {validator_result}
        - BidGPT: {bid_result}
        Dialogue Log between ValidatorGPT and MarketGPT: {dialogue_log}
        Your task is to:
        1. Evaluate all results, explanations, and the dialogue log to determine the most logical final cost.
        2. If a discrepancy remains unresolved, resolve it based on the full context.
        3. Provide a detailed reasoning for your final decision.
        Return the result in JSON format with:
        - final_cost: the final cost estimate in USD
        - cost_breakdown: a detailed breakdown of the cost into direct and indirect components with unit costs
        - reasoning: a detailed explanation of your final decision
        """
        try:
            with st.spinner("جارٍ دمج النتائج النهائية..."):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are CoordinatorGPT, a cautious pricing engineer tasked with coordinating results from multiple agents."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7,
                    timeout=30
                )
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"Error in coordinate_results: {e}")
            return {"error": "فشل في دمج النتائج النهائية"}

    def analyze_and_estimate(self, task_description: str) -> Dict:
        """Estimate cost with cautious pricing logic and Monte Carlo simulation (original method)."""
        if task_description in self.price_history:
            entry = self.price_history[task_description]
            timestamp = entry["timestamp"]
            current_time = datetime.now().timestamp()
            if current_time - timestamp < 90 * 24 * 60 * 60:  # 90 days in seconds
                return {
                    "tasks": entry.get("tasks", []),
                    "contradictions": entry.get("contradictions", []),
                    "missing_details": entry.get("missing_details", []),
                    "total_cost": entry["cost"],
                    "cost_breakdown": entry.get("cost_breakdown", {}),
                    "reasoning": "تم استرجاع التقدير من البيانات التاريخية (خلال 90 يومًا)."
                }

        scope_analysis = self.validate_scope(task_description)
        contradictions = scope_analysis["contradictions"]
        tasks = scope_analysis["tasks"]
        missing_details = scope_analysis.get("missing_details", [])

        if contradictions:
            return {
                "tasks": tasks,
                "contradictions": contradictions,
                "missing_details": missing_details,
                "total_cost": None,
                "cost_breakdown": {},
                "reasoning": "تم اكتشاف تناقضات، يرجى حلها قبل تقدير التكلفة."
            }

        if missing_details:
            st.warning("تم اكتشاف تفاصيل مفقودة قد تؤثر على دقة التقدير:")
            for i, detail in enumerate(missing_details):
                st.write(f"Missing Detail {i+1}: {detail}")
            st.info("يمكنك متابعة التقدير، لكن يُنصح بإضافة التفاصيل المفقودة للحصول على نتائج أدق.")

        helper_data = fetch_helper_data()
        costs = []
        reasonings = []
        cost_breakdowns = []
        for i in range(10):  # تقليل عدد التكرارات إلى 10
            st.info(f"جارٍ تشغيل المحاكاة {i+1} من 10...")
            result = self.estimate_cost_once(task_description, helper_data)
            if result is not None and "total_cost" in result:
                costs.append(result["total_cost"])
                reasonings.append(result["reasoning"])
                cost_breakdowns.append(result.get("cost_breakdown", {}))

        historical_costs = [entry["cost"] for entry in self.price_history.values()]
        validator_result = self.validate_cost(costs, historical_costs, task_description, helper_data)
        if "error" in validator_result:
            return {"error": validator_result["error"]}

        final_cost = sum(costs) / len(costs) if costs else 0
        cost_breakdown = cost_breakdowns[-1] if cost_breakdowns else {}
        reasoning = validator_result.get("reasoning", "تم تقدير التكلفة بناءً على المحاكاة.")

        result = {
            "tasks": tasks,
            "contradictions": contradictions,
            "missing_details": missing_details,
            "total_cost": final_cost,
            "cost_breakdown": cost_breakdown,
            "reasoning": reasoning
        }
        self.price_history[task_description] = {
            "cost": final_cost,
            "cost_breakdown": cost_breakdown,
            "tasks": tasks,
            "contradictions": contradictions,
            "missing_details": missing_details,
            "timestamp": datetime.now().timestamp()
        }
        st.session_state.price_history = self.price_history

        st.session_state.projects.append({
            "task_description": task_description,
            "total_cost": final_cost,
            "timestamp": datetime.now().timestamp()
        })

        return result

    def analyze_and_estimate_multi_gpt(self, task_description: str) -> Dict:
        """Estimate cost using Multi-GPT Architecture with internal dialogue."""
        if task_description in self.price_history:
            entry = self.price_history[task_description]
            timestamp = entry["timestamp"]
            current_time = datetime.now().timestamp()
            if current_time - timestamp < 90 * 24 * 60 * 60:  # 90 days in seconds
                return {
                    "tasks": entry.get("tasks", []),
                    "contradictions": entry.get("contradictions", []),
                    "missing_details": entry.get("missing_details", []),
                    "total_cost": entry["cost"],
                    "cost_breakdown": entry.get("cost_breakdown", {}),
                    "reasoning": "تم استرجاع التقدير من البيانات التاريخية (خلال 90 يومًا)."
                }

        # Step 1: ScopeGPT analyzes the scope of work
        scope_result = self.validate_scope(task_description)
        contradictions = scope_result["contradictions"]
        tasks = scope_result["tasks"]
        missing_details = scope_result.get("missing_details", [])

        if contradictions:
            return {
                "tasks": tasks,
                "contradictions": contradictions,
                "missing_details": missing_details,
                "total_cost": None,
                "cost_breakdown": {},
                "reasoning": "تم اكتشاف تناقضات، يرجى حلها قبل تقدير التكلفة."
            }

        if missing_details:
            st.warning("تم اكتشاف تفاصيل مفقودة قد تؤثر على دقة التقدير:")
            for i, detail in enumerate(missing_details):
                st.write(f"Missing Detail {i+1}: {detail}")
            st.info("يمكنك متابعة التقدير، لكن يُنصح بإضافة التفاصيل المفقودة للحصول على نتائج أدق.")

        # Step 2: MarketGPT estimates the cost
        helper_data = fetch_helper_data()
        costs = []
        reasonings = []
        cost_breakdowns = []
        for i in range(10):  # تقليل عدد التكرارات إلى 10
            st.info(f"جارٍ تشغيل المحاكاة {i+1} من 10...")
            result = self.estimate_cost_once(task_description, helper_data)
            if result is not None and "total_cost" in result:
                costs.append(result["total_cost"])
                reasonings.append(result["reasoning"])
                cost_breakdowns.append(result.get("cost_breakdown", {}))

        market_result = {
            "total_cost": sum(costs) / len(costs) if costs else 0,
            "cost_breakdown": cost_breakdowns[-1] if cost_breakdowns else {},
            "reasoning": reasonings[-1] if reasonings else "تم تقدير التكلفة بناءً على المحاكاة."
        }

        # Step 3: ValidatorGPT validates the cost
        historical_costs = [entry["cost"] for entry in self.price_history.values()]
        validator_result = self.validate_cost(costs, historical_costs, task_description, helper_data)
        if "error" in validator_result:
            return {"error": validator_result["error"]}

        # Step 4: Internal dialogue between ValidatorGPT and MarketGPT (1 round)
        dialogue_log = {}
        if not validator_result.get("is_valid", True):
            clarification_request = validator_result.get("clarification_request", "")
            if clarification_request:
                market_clarification = self.request_clarification(task_description, helper_data, clarification_request)
                if "error" in market_clarification:
                    return {"error": market_clarification["error"]}
                dialogue_log["ValidatorGPT_to_MarketGPT"] = [
                    {"request": clarification_request, "response": market_clarification}
                ]
                market_result = market_clarification
                validator_result["is_valid"] = True  # Assume resolved unless further validation is needed

        # Step 5: BidGPT compares with bids (if applicable)
        bid_result = {"estimated_cost": market_result["total_cost"], "actual_bid": None, "deviation_percent": None, "recommendation": "No bid provided."}

        # Step 6: CoordinatorGPT coordinates the results
        if not validator_result.get("is_valid", True):
            coordinated_result = self.coordinate_results(task_description, scope_result, market_result, validator_result, bid_result, dialogue_log)
            if "error" in coordinated_result:
                return {"error": coordinated_result["error"]}
        else:
            coordinated_result = {
                "final_cost": market_result["total_cost"],
                "cost_breakdown": market_result["cost_breakdown"],
                "reasoning": "تم قبول التكلفة بعد الحوار الداخلي: " + market_result["reasoning"]
            }

        result = {
            "tasks": tasks,
            "contradictions": contradictions,
            "missing_details": missing_details,
            "total_cost": coordinated_result["final_cost"],
            "cost_breakdown": coordinated_result["cost_breakdown"],
            "reasoning": coordinated_result["reasoning"]
        }
        self.price_history[task_description] = {
            "cost": coordinated_result["final_cost"],
            "cost_breakdown": coordinated_result["cost_breakdown"],
            "tasks": tasks,
            "contradictions": contradictions,
            "missing_details": missing_details,
            "timestamp": datetime.now().timestamp()
        }
        st.session_state.price_history = self.price_history

        st.session_state.projects.append({
            "task_description": task_description,
            "total_cost": coordinated_result["final_cost"],
            "timestamp": datetime.now().timestamp()
        })

        return result

# Dashboard statistics from session state
def get_dashboard_stats():
    total_projects = len(st.session_state.get("projects", []))
    total_cost_estimated = sum(project["total_cost"] for project in st.session_state.get("projects", []) if project["total_cost"] is not None)
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

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

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

elif st.session_state.page == "estimate_cost":
    st.header("Estimate Cost")
    
    st.markdown("💡 **تلميح**: تأكد من أن نطاق العمل يحتوي على تفاصيل واضحة حول المواد، الجدول الزمني، والموقع للحصول على تقدير دقيق.")

    st.subheader("تفاصيل إضافية (اختياري)")
    project_location = st.text_input("الموقع الجغرافي للمشروع (مثل: الرياض، المملكة العربية السعودية):")
    project_timeline = st.text_input("الجدول الزمني للمشروع (مثل: 6 أشهر):")
    material_specifications = st.text_area("مواصفات المواد (مثل: استخدام مواد قياسية):")

    uploaded_files = st.file_uploader("Upload Scope of Work (Word, Excel, PDF)", type=["docx", "xlsx", "pdf"], accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success("Files uploaded successfully!")
        st.info("اضغط على زر 'Proceed to Estimate Cost' لتحليل نطاق العمل وتقدير التكلفة.")

    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        st.subheader("Scope Analysis")
        estimator = CostEstimator()
        contradictions = []
        task_description = ""
        for uploaded_file in st.session_state.uploaded_files:
            content = estimator.read_file(uploaded_file)
            task_description += f"File: {uploaded_file.name}\n{content}\n"
        if project_location:
            task_description += f"\nProject Location: {project_location}"
        if project_timeline:
            task_description += f"\nProject Timeline: {project_timeline}"
        if material_specifications:
            task_description += f"\nMaterial Specifications: {material_specifications}"

        with st.spinner("جارٍ تحليل نطاق العمل..."):
            scope_analysis = estimator.validate_scope(task_description)
            contradictions.extend(scope_analysis["contradictions"])
            st.session_state.tasks = scope_analysis["tasks"]
            st.session_state.missing_details = scope_analysis.get("missing_details", [])

        st.session_state.task_description = task_description

        if contradictions:
            st.subheader("Contradictions Found")
            st.warning("تم العثور على تناقضات في نطاق العمل. يرجى مراجعة التناقضات أدناه وتقديم توضيحات إذا لزم الأمر:")
            for i, contradiction in enumerate(contradictions):
                st.write(f"Contradiction {i+1}: {contradiction}")
                user_response = st.text_input(f"Response to contradiction {i+1}:", key=f"contradiction_{i}")
                if user_response:
                    st.session_state[f"contradiction_response_{i}"] = user_response
                    st.success(f"تم حفظ ردك على التناقض {i+1} بنجاح!")
        elif not st.session_state.tasks:
            st.warning("لم تظهر أي نتائج. يرجى المحاولة مرة أخرى أو التحقق من السجلات لمعرفة الأخطاء.")
        else:
            st.subheader("Extracted Tasks")
            for i, task in enumerate(st.session_state.tasks):
                st.write(f"Task {i+1}: {task}")
            if st.session_state.missing_details:
                st.subheader("Missing Details")
                for i, detail in enumerate(st.session_state.missing_details):
                    st.write(f"Missing Detail {i+1}: {detail}")

        if st.button("Proceed to Estimate Cost"):
            if st.session_state.is_processing:
                st.warning("جارٍ المعالجة... يرجى الانتظار.")
            else:
                st.session_state.is_processing = True
                try:
                    if "uploaded_files" not in st.session_state or not st.session_state.uploaded_files:
                        st.error("يرجى رفع ملف نطاق العمل أولاً!")
                    else:
                        final_description = st.session_state.task_description
                        if "contradiction_response_0" in st.session_state:
                            final_description += f" with user responses: {st.session_state['contradiction_response_0']}"
                        with st.spinner("جارٍ تقدير التكلفة... قد يستغرق هذا بضع ثوانٍ"):
                            result = estimator.analyze_and_estimate_multi_gpt(final_description)
                        st.session_state.estimation_result = result
                        st.session_state.page = "estimation_result"
                finally:
                    st.session_state.is_processing = False

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
                st.warning("تم اكتشاف تناقضات في نطاق العمل. يرجى مراجعة التناقضات أدناه وتقديم توضيحات إضافية:")
                for i, contradiction in enumerate(result["contradictions"]):
                    st.write(f"Contradiction {i+1}: {contradiction}")
                user_response = st.text_area("أدخل توضيحات لمعالجة التناقضات:", key="contradiction_response")
                if st.button("إعادة تقدير التكلفة بعد التوضيح"):
                    if user_response:
                        final_description = st.session_state.task_description + f"\nUser clarifications: {user_response}"
                        with st.spinner("جارٍ إعادة تقدير التكلفة..."):
                            estimator = CostEstimator()
                            result = estimator.analyze_and_estimate_multi_gpt(final_description)
                            st.session_state.estimation_result = result
                            st.experimental_rerun()
                    else:
                        st.error("يرجى إدخال توضيحات لحل التناقضات قبل إعادة التقدير.")
            else:
                st.write("No contradictions found.")
            if result.get("missing_details"):
                st.subheader("Missing Details")
                for i, detail in enumerate(result["missing_details"]):
                    st.write(f"Missing Detail {i+1}: {detail}")
            if result["total_cost"] is not None:
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
                st.info("يمكنك الآن العودة إلى لوحة التحكم أو تحليل عطاءات إضافية من خلال قسم 'Analyze Bids'.")
            else:
                st.warning("لم يتم تقدير التكلفة بسبب التناقضات أو مشكلات أخرى. يرجى حل التناقضات أو التحقق من السجلات.")
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"

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
            st.session_state.bids.append({
                "task_description": task_description,
                "actual_bid": actual_bid,
                "timestamp": datetime.now().timestamp()
            })
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"

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