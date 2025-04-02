
# CostimAIze V8 - النسخة الرسمية المعتمدة
# تم تطويره بالكامل بناءً على المحادثات ٣، ٤، ٥، ٦، والدفعة النهائية من المحادثة ٨
# كل طبقة معرفة كوحدة مستقلة قابلة للتشغيل داخل بنية طبقية (Modular Layered Architecture)
# يديره منسق مركزي (AI Orchestrator)

# ------------------------------
# 1. AI Estimator Identity & Learning Engine
# ------------------------------
class AIEstimatorIdentity:
    def __init__(self, historical_db):
        self.historical_db = historical_db
        self.memory = []

    def match_historical_price(self, component, project_type):
        matches = [p for p in self.historical_db if p['type'] == project_type and p['component'] == component]
        return matches[0]['price'] if matches else None

    def learn(self, project_data):
        self.memory.append(project_data)

    def get_insight(self):
        return f"Learned from {len(self.memory)} past projects."

# ------------------------------
# 2. SOW Understanding Layer
# ------------------------------
class SOWUnderstandingLayer:
    def run(self, input_text):
        parsed_scope = {
            "components": ["Transformer", "GIS", "Protection", "SAS", "HVAC", "Civil"]
        }
        return parsed_scope

# ------------------------------
# 3. Missing Info Estimation
# ------------------------------
class MissingInfoEstimator:
    def run(self, parsed_scope):
        parsed_scope['cable_length'] = 350
        return parsed_scope

# ------------------------------
# 4. SOW Consistency Checker & Inquiry Engine
# ------------------------------
class SOWConsistencyChecker:
    def run(self, scope):
        inquiries = []
        if 'Transformer' in scope['components'] and 'capacity' not in scope:
            inquiries.append("Capacity missing for transformer")
        return inquiries

# ------------------------------
# 5. GPT Market Estimator
# ------------------------------
class GPTMarketEstimator:
    def estimate(self, component):
        return {
            "Transformer": 5100000,
            "GIS": 4000000,
            "Protection": 950000,
            "SAS": 1350000,
            "HVAC": 650000,
            "Civil": 8700000
        }.get(component, 1000000)

# ------------------------------
# 6. Smart Cautious Pricing Engine (Merged with Pricing Context)
# ------------------------------
class SmartCautiousPricing:
    def run(self, market_prices, historical_prices):
        hybrid_prices = {}
        for comp, market_price in market_prices.items():
            hist_price = historical_prices.get(comp)
            if hist_price:
                hybrid_prices[comp] = round((0.7 * market_price) + (0.3 * hist_price))
            else:
                hybrid_prices[comp] = market_price
        return hybrid_prices

# ------------------------------
# 7. Bid Price Analyzer
# ------------------------------
class BidPriceAnalyzer:
    def analyze(self, contractor_prices, reference_prices):
        report = {}
        for comp in contractor_prices:
            deviation = contractor_prices[comp] - reference_prices.get(comp, 0)
            report[comp] = deviation
        return report

# ------------------------------
# 8. Smart Overpricing/Underpricing Handling
# ------------------------------
class PriceDeviationInterpreter:
    def interpret(self, deviation_report):
        interpretations = {}
        for comp, value in deviation_report.items():
            if abs(value) < 100000:
                interpretations[comp] = "Acceptable"
            elif value > 0:
                interpretations[comp] = "Overpriced"
            else:
                interpretations[comp] = "Underpriced"
        return interpretations

# ------------------------------
# 9. Intelligent Bid Verdict Generator
# ------------------------------
class BidVerdictGenerator:
    def verdict(self, interpreted_report):
        if "Overpriced" in interpreted_report.values():
            return "Conditionally Acceptable"
        return "Acceptable"

# ------------------------------
# 10. Visual Report Generator
# ------------------------------
class VisualReportGenerator:
    def generate(self, all_data):
        print("\n=== AI Final Report ===")
        for key, val in all_data.items():
            print(f"{key}: {val}")

# ------------------------------
# 11. AI Time Tracker & Performance Logger
# ------------------------------
import time
class AITracker:
    def __init__(self):
        self.logs = []

    def track(self, layer_name, start, end):
        self.logs.append({"layer": layer_name, "time_sec": round(end - start, 2)})

    def report(self):
        return self.logs

# ------------------------------
# 12. AI Orchestrator
# ------------------------------
class CostimAIzeOrchestrator:
    def __init__(self):
        self.tracker = AITracker()
        self.layers = {
            "sow": SOWUnderstandingLayer(),
            "missing": MissingInfoEstimator(),
            "check": SOWConsistencyChecker(),
            "market": GPTMarketEstimator(),
            "price": SmartCautiousPricing(),
            "verdict": BidVerdictGenerator(),
            "report": VisualReportGenerator()
        }

    def run_estimation(self, sow_text, historical_db):
        start = time.time()

        identity = AIEstimatorIdentity(historical_db)
        scope = self.layers['sow'].run(sow_text)
        scope = self.layers['missing'].run(scope)
        inquiries = self.layers['check'].run(scope)

        market_prices = {comp: self.layers['market'].estimate(comp) for comp in scope['components']}
        hist_prices = {comp: identity.match_historical_price(comp, '132kV') for comp in scope['components']}
        final_estimates = self.layers['price'].run(market_prices, hist_prices)

        end = time.time()
        self.tracker.track("Full Estimation", start, end)

        self.layers['report'].generate({
            "Scope": scope,
            "Inquiries": inquiries,
            "Market Prices": market_prices,
            "Historical Prices": hist_prices,
            "Final Estimates": final_estimates,
            "Logs": self.tracker.report()
        })

# ------------------------------
# Example execution
# ------------------------------
if __name__ == "__main__":
    orchestrator = CostimAIzeOrchestrator()
    sample_sow = "Supply and install 2 Transformers, GIS, Protection and Control systems, HVAC and Civil works."
    historical_data = [
        {"type": "132kV", "component": "Transformer", "price": 4900000},
        {"type": "132kV", "component": "GIS", "price": 3950000},
        {"type": "132kV", "component": "Protection", "price": 890000},
        {"type": "132kV", "component": "SAS", "price": 1300000},
        {"type": "132kV", "component": "HVAC", "price": 640000},
        {"type": "132kV", "component": "Civil", "price": 8600000}
    ]
    orchestrator.run_estimation(sample_sow, historical_data)
