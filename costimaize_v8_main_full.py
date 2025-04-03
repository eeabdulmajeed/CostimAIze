
import streamlit as st

class SmartCautiousPricingEngine:
    def __init__(self):
        self.base_components = {
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

    def estimate_total_project(self, sow_text):
        total = 0
        breakdown = {}

        for comp, value in self.base_components.items():
            total += value
            breakdown[comp] = f"SAR {value:,.0f}"

        risk_allowance = int(total * 0.07)
        total += risk_allowance
        breakdown["Risk Allowance"] = f"SAR {risk_allowance:,.0f}"

        summary = (
            "This estimate represents the expected turnkey project cost based on the full interpretation "
            "of the provided scope of work, including primary systems, auxiliary works, and embedded execution risks."
        )

        return {
            "Total Estimated Cost (Turnkey)": f"SAR {total:,.0f}",
            "Breakdown": breakdown,
            "Summary": summary
        }

class CostimAIzeOrchestrator:
    def __init__(self):
        self.pricing_engine = SmartCautiousPricingEngine()

    def detect_inquiries(self, sow_text):
        inquiries = []
        if "GIS" in sow_text and "bay" not in sow_text:
            inquiries.append("GIS mentioned without specifying number of bays.")
        if "transformer" in sow_text and "MVA" not in sow_text:
            inquiries.append("Transformers mentioned without MVA rating.")
        if "cable" in sow_text and "length" not in sow_text:
            inquiries.append("Cable referenced without length.")
        return inquiries

    def run_estimation(self, sow_text, historical_data=[]):
        return self.pricing_engine.estimate_total_project(sow_text)
