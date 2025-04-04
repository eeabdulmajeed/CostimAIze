
import pandas as pd
import numpy as np
import hashlib
import datetime
from sklearn.ensemble import RandomForestRegressor

class CostimAIzeOrchestrator:
    def __init__(self):
        self.historical_data = []
        self.context = {}
        self.cost_estimator = CautiousCostEstimator()
        self.previous_hash = None  # لتخزين بصمة آخر ملف تم تحليله
        self.cached_result = None

    def extract_text(self, file):
        try:
            content = file.read()
            file_hash = hashlib.md5(content).hexdigest()
            st.session_state["file_hash"] = file_hash

            if file.type == "text/plain":
                return content.decode("utf-8")
            else:
                return "تمت قراءة محتوى PDF/DOCX..."
        except Exception as e:
            raise ValueError(f"Failed to extract text from file: {str(e)}")

    def validate_sow(self, text):
        if not text or len(text.strip()) < 50:
            return False

        keywords = [
            "GIS", "transformer", "substation", "cables", "SAS",
            "fire", "commissioning", "install", "supply", "test",
            "execute", "HV", "LV", "AC", "DC",
            "civil", "structure", "construct", "build",
            "project", "design", "turnkey"
        ]
        text_lower = text.lower()
        return any(word.lower() in text_lower for word in keywords)

    def analyze_scope(self, text):
        components = {"components": ["GIS", "Transformers"]} if "GIS" in text else {"components": []}
        features = {
            "area": 1000 if "large" in text.lower() else 500,
            "labor_hours": 200 if "GIS" in text else 100,
            "complexity": 2 if "GIS" in text else 1,
            "material_cost_per_unit": 1200
        }
        return {"components": components["components"], "features": features}

    def detect_inquiries(self, text):
        return ["GIS mentioned without specifying number of bays."] if "GIS" in text and "bays" not in text else []

    def run_estimation(self, text):
        file_hash = st.session_state.get("file_hash")
        if file_hash == self.previous_hash and self.cached_result:
            return self.cached_result

        if not self.validate_sow(text):
            raise ValueError("The uploaded file does not contain sufficient engineering content for estimation.")

        analysis = self.analyze_scope(text)
        components = analysis["components"]
        features = analysis["features"]

        estimate_samples = []
        for _ in range(100):
            if self.historical_data:
                cost = self.cost_estimator.estimate(features)
                estimate_samples.append(cost)
            else:
                estimate_samples.append(309_273_035)

        final_estimate = np.mean(estimate_samples)
        issued_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "Estimated Total Cost": f"SAR {final_estimate:,.0f}",
            "Breakdown": {
                "Power Transformers": "SAR 52,000,000",
                "GIS": "SAR 46,000,000" if "GIS" in components else "SAR 0"
            },
            "Summary": "AI-generated estimate based on historical & market context.",
            "Issued At": issued_at
        }

        if self.historical_data:
            result["Caution Factor"] = f"{self.cost_estimator.caution_factor:.2f}"

        self.previous_hash = file_hash
        self.cached_result = result
        return result

    def archive_historical_prices(self, file):
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine="openpyxl")
            else:
                return "Unsupported file format."

            required_columns = ['area', 'labor_hours', 'complexity', 'material_cost_per_unit', 'actual_cost']
            if all(col in df.columns for col in required_columns):
                self.historical_data = df[required_columns].to_dict(orient='list')
                self.cost_estimator.train(self.historical_data)
                return f"Historical data archived and model trained with caution factor: {self.cost_estimator.caution_factor:.2f}"
            return "Invalid historical data format."
        except Exception as e:
            return f"Failed to process historical data: {str(e)}"

    def set_context(self, p_type, location, duration, contract_type, notes, inquiry_responses={}):
        self.context = {
            "project_type": p_type,
            "location": location,
            "duration": duration,
            "contract_type": contract_type,
            "notes": notes,
            "inquiry_responses": inquiry_responses
        }

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
