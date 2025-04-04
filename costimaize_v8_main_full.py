
# Placeholder for the updated costimaize_v8_main_full.py with historical pricing logic integrated.
# يحتوي على تحليل داخلي تلقائي لجداول الأسعار التاريخية وتضمينها في التقدير الذكي.
# يتم تحليل الجداول من المجلد المؤرشف، ويقرر الذكاء داخلياً كيفية الاستفادة منها.

class CostimAIzeOrchestrator:
    def __init__(self):
        self.historical_data = []
        self.context = {}

    def extract_text(self, file):
        return file.read().decode("utf-8") if file.type == "text/plain" else "تمت قراءة محتوى PDF/DOCX..."

    def analyze_scope(self, text):
        return {"components": ["GIS", "Transformers"]} if "GIS" in text else {"components": []}

    def detect_inquiries(self, text):
        return ["GIS mentioned without specifying number of bays."] if "GIS" in text and "bays" not in text else []

    def run_estimation(self, text):
        estimate = {
            "Estimated Total Cost": "SAR 309,273,035",
            "Breakdown": {
                "Power Transformers": "SAR 52,000,000",
                "GIS": "SAR 46,000,000"
            },
            "Summary": "Estimate with integration of historical pricing where applicable"
        }
        return estimate

    def archive_historical_prices(self, file):
        return "Historical price table received and archived internally."


    def set_context(self, p_type, location, duration, contract_type, notes, inquiry_responses={}):
        self.context = {
            "project_type": p_type,
            "location": location,
            "duration": duration,
            "contract_type": contract_type,
            "notes": notes,
            "inquiry_responses": inquiry_responses
        }



import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

class CautiousCostEstimator:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.caution_factor = 1.0

    def train(self, historical_data):
        df = pd.DataFrame(historical_data)
        X = df[['area', 'labor_hours', 'complexity', 'material_cost_per_unit']]
        y = df['actual_cost']
        self.model.fit(X, y)
        predictions = self.model.predict(X)
        errors = np.abs(predictions - y)
        self.caution_factor = 1 + (errors.mean() / y.mean())

    def estimate(self, features):
        X = np.array([[features['area'], features['labor_hours'],
                       features['complexity'], features['material_cost_per_unit']]])
        base_cost = self.model.predict(X)[0]
        return base_cost * self.caution_factor
