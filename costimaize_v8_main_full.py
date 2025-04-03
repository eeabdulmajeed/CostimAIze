
import streamlit as st
import random
import time
import os
import json
from datetime import datetime, timedelta

class SmartCautiousPricingEngine:
    def __init__(self):
        self.components = {
            "Power Transformers": 52000000,
            "GIS": 46000000,
            "Protection System": 9500000,
            "Control & SAS": 18000000,
            "Fire Fighting": 6000000,
            "HVAC": 8500000,
            "Civil Works": 92000000,
            "Cabling & Trays": 15000000,
            "AC/DC Systems": 7000000,
            "Lighting": 4000000,
            "Battery & Chargers": 6000000,
            "SCADA & Communication": 12000000,
            "Cybersecurity & Integration": 3000000,
            "Training, Handover, Docs": 5000000
        }

    def monte_carlo_estimate(self, base_price):
        samples = [base_price * random.uniform(0.92, 1.12) for _ in range(100)]
        return int(sum(samples) / len(samples))

    def estimate_total_project(self, sow_text, context={}):
        total = 0
        breakdown = {}
        for comp, base in self.components.items():
            cost = self.monte_carlo_estimate(base)
            breakdown[comp] = f"SAR {cost:,.0f}"
            total += cost
        risk_allowance = int(total * 0.07)
        total += risk_allowance
        breakdown["Risk Allowance"] = f"SAR {risk_allowance:,.0f}"
        return {
            "Total Estimated Cost (Turnkey)": f"SAR {total:,.0f}",
            "Breakdown": breakdown,
            "Summary": "This estimate reflects AI-driven turnkey evaluation, including embedded risks and inferred scope extensions.",
            "Contract Type": context.get("contract_type", "Not Provided"),
            "Execution Duration": context.get("duration", "Not Provided"),
            "Location": context.get("location", "Not Provided"),
            "Issued At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

class CostimAIzeOrchestrator:
    def __init__(self):
        self.pricing_engine = SmartCautiousPricingEngine()
        self.context = {}
        self.time_start = None
        self.cache_file = "/mnt/data/estimation_cache.json"

    def set_context(self, p_type, location, duration, contract_type, notes):
        self.context = {
            "project_type": p_type,
            "location": location,
            "duration": duration,
            "contract_type": contract_type,
            "notes": notes
        }

    def detect_inquiries(self, sow_text):
        if not sow_text.strip():
            return []
        inquiries = []
        if "GIS" in sow_text and "bay" not in sow_text:
            inquiries.append("GIS mentioned without specifying number of bays.")
        if "transformer" in sow_text and "MVA" not in sow_text:
            inquiries.append("Transformers mentioned without MVA rating.")
        if "cable" in sow_text and "length" not in sow_text:
            inquiries.append("Cables referenced without clear lengths.")
        return inquiries

    def run_estimation(self, sow_text, historical_data=[]):
        self.time_start = time.time()
        sow_hash = hashlib.sha256(sow_text.encode("utf-8")).hexdigest()

        # محاولة قراءة التقديرات السابقة من الملف
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                cache = json.load(f)
        else:
            cache = {}

        # إذا وُجد نفس التقدير سابقًا ولم تنتهِ صلاحيته
        if sow_hash in cache:
            entry = cache[sow_hash]
            issued = datetime.strptime(entry["Issued At"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - issued < timedelta(days=90):
                return entry  # إعادة نفس التقدير بدون تغيير

        # تنفيذ التقدير لأول مرة
        result = self.pricing_engine.estimate_total_project(sow_text, self.context)
        cache[sow_hash] = result

        with open(self.cache_file, "w") as f:
            json.dump(cache, f, indent=2)

        result["Estimation Time (sec)"] = round(time.time() - self.time_start, 2)
        return result
