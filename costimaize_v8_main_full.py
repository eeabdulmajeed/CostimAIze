import os
import csv
from datetime import datetime, timedelta
import hashlib

import pandas as pd
import numpy as np
import hashlib
import datetime
from sklearn.ensemble import RandomForestRegressor

class CostimAIzeOrchestrator:
    def __init__(self):
        self.historical_data = []
        self.context = {}
        self.historical_contexts = []
        self.cost_estimator = CautiousCostEstimator()
        self.previous_hash = None  # لتخزين بصمة آخر ملف تم تحليله
        self.cached_result = None

    def extract_text(self, file):
        try:
            content = file.read()
            file_hash = hashlib.md5(content).hexdigest()
        except Exception as e:
            pass
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
        text_lower = text.lower()
        inquiries = []

        # ذكاء اصطناعي بسيط لاستنتاج وجود فجوات منطقية
        if "design" in text_lower and "construct" not in text_lower:
            inquiries.append("Design mentioned but construction not confirmed.")
        if "install" in text_lower and "test" not in text_lower:
            inquiries.append("Installation mentioned without test procedures.")
        if "commissioning" not in text_lower and "handover" in text_lower:
            inquiries.append("Handover mentioned but commissioning missing.")
        if "scope of work" in text_lower and len(text_lower) < 300:
            inquiries.append("Scope of work section appears too brief.")
        if "project" in text_lower and "contractor" not in text_lower:
            inquiries.append("Project mentioned without identifying the responsible contractor.")

        return inquiries
    
    def run_estimation(self, text):
        # فحص ما إذا تم التقدير مسبقًا خلال أقل من 90 يومًا
        hash_key = hashlib.md5(text.encode()).hexdigest()
        log_file = "/mnt/data/estimation_log.csv"
        if os.path.exists(log_file):
            import pandas as pd
            df = pd.read_csv(log_file)
            match = df[df["hash"] == hash_key]
            if not match.empty:
                last_time = datetime.strptime(match.iloc[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - last_time).days < 90:
                    result = {
                        "Estimated Total Cost": match.iloc[0]["estimated_cost"],
                        "Reused From Archive": True,
                        "Issued At": match.iloc[0]["timestamp"]
                    }
                    return result

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
            "Inquiry Responses": self.context.get("inquiry_responses", {}),
        "Summary": "AI-generated estimate based on historical & market context.",
            "Issued At": issued_at
        }

        if self.historical_data:
            result["Caution Factor"] = f"{self.cost_estimator.caution_factor:.2f}"

        self.previous_hash = file_hash
        
        # تحليل الردود على الاستفسارات
        responses = self.context.get("inquiry_responses", {})
        incomplete_responses = sum(1 for r in responses.values() if not r.strip())
        if incomplete_responses > 0:
            penalty_factor = 1 + (0.02 * incomplete_responses)
            final_estimate *= penalty_factor
            result["Adjusted for Inquiry Gaps"] = f"Increased by {int((penalty_factor - 1)*100)}% due to {incomplete_responses} unanswered inquiries."

        
        # تحليل نصوص الردود لمحاولة تحسين التقدير
        safe_keywords = ["completed", "confirmed", "available", "supplied", "tested", "ready"]
        responses_text = " ".join(responses.values()).lower()
        safe_hits = sum(1 for word in safe_keywords if word in responses_text)
        if safe_hits > 0:
            adjustment_factor = 1 - (0.01 * safe_hits)
            final_estimate *= adjustment_factor
            result["Adjusted for Reassuring Responses"] = f"Reduced by {int((1 - adjustment_factor) * 100)}% due to positive confirmations in responses."

        
        used_model = self.cost_estimator.trained
        result["Used Historical Model"] = used_model
        result["Historical Data Size"] = len(self.historical_data)
        if used_model and hasattr(self.cost_estimator, 'confidence_level'):
            result["Model Confidence"] = f"{self.cost_estimator.confidence_level:.1f}%"

        
        # حفظ التقدير الجديد في سجل CSV
        log_entry = [hash_key, issued_at, f"SAR {final_estimate:,.0f}"]
        file_exists = os.path.exists(log_file)
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["hash", "timestamp", "estimated_cost"])
            writer.writerow(log_entry)

        self.cached_result = result
        return result

    
    def archive_historical_prices(self, file, metadata=None):
        try:
            import pandas as pd
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine="openpyxl")
            else:
        except Exception as e:
            pass
                return "Unsupported file format."

            required_columns = ['area', 'labor_hours', 'complexity', 'material_cost_per_unit', 'actual_cost']
            for col in required_columns:
                if col not in df.columns:
                    return f"Missing required column: {col}"

            df = df.dropna()
            df = df[df['actual_cost'] > 0]
            df = df[df['area'] > 0]
            df = df[df['labor_hours'] > 0]

            if df.empty:
                return "No valid data available after cleaning."

            self.historical_data = df[required_columns].to_dict(orient='list')
            
            if metadata:
                self.historical_contexts.append(metadata)
            self.cost_estimator.train(self.historical_data)
            return f"Model trained. Caution factor: {self.cost_estimator.caution_factor:.2f} | Records used: {len(df)}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine="openpyxl")
            else:
                return "Unsupported file format."

            required_columns = ['area', 'labor_hours', 'complexity', 'material_cost_per_unit', 'actual_cost']
            if all(col in df.columns for col in required_columns):
                self.historical_data = df[required_columns].to_dict(orient='list')
                
            if metadata:
                self.historical_contexts.append(metadata)
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
        self.confidence_level = 100 * (1 - errors.mean() / y.mean())

    def estimate(self, features):
        X = np.array([[features['area'], features['labor_hours'],
                       features['complexity'], features['material_cost_per_unit']]])
        base_cost = self.model.predict(X)[0]
        return base_cost * self.caution_factor


    def analyze_bid(self, sow_text, contractor_data):
        if not self.validate_sow(sow_text):
            return {"error": "Invalid SOW. Cannot perform bid analysis."}

        components = self.analyze_scope(sow_text)["components"]
        reference_prices = {
            "GIS": 46000000,
            "Transformers": 52000000,
            "Protection": 9500000
        }

        results = []
        for item in contractor_data:
            desc = item.get("description", "").lower()
            qty = float(item.get("quantity", 1))
            unit_price = float(item.get("unit_price", 0))

            matched_ref = next((ref for key, ref in reference_prices.items() if key.lower() in desc), None)
            if matched_ref:
                total_ref = matched_ref * qty
                total_bid = unit_price * qty
                delta = total_bid - total_ref
                percent = 100 * delta / total_ref
                status = "Overpriced" if percent > 10 else "Underpriced" if percent < -10 else "Fair"

                results.append({
                    "description": item["description"],
                    "qty": qty,
                    "unit_price": unit_price,
                    "reference_price": matched_ref,
                    "difference": f"SAR {delta:,.2f}",
                    "percentage": f"{percent:.2f}%",
                    "status": status
                })

        return {
            "analysis": results,
            "summary": {
                "total_items": len(results),
                "overpriced": sum(1 for r in results if r["status"] == "Overpriced"),
                "fair": sum(1 for r in results if r["status"] == "Fair"),
                "underpriced": sum(1 for r in results if r["status"] == "Underpriced")
            }
        }
