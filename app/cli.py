import sys
import json
from app.parser import DataParser
from app.engine import AnalyticsEngine
from app.metrics.mrr import MonthlyMRRMetric
from app.metrics.churn import MonthlyChurnMetric
from app.metrics.cohorts import Cohorts

def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <customers.csv> <subscriptions.csv> <output.json>")
        sys.exit(1)

    #  FIX: This correctly assigns each specific file path to its own variable.
    cust_path = sys.argv[1]  # The 1st argument (e.g., "customers.csv")
    subs_path = sys.argv[2]  # The 2nd argument (e.g., "subscriptions.csv")
    out_path = sys.argv[3]   # The 3rd argument (e.g., "output.json")


    try:
        # Load and Validate Data
        df_cust, df_subs = DataParser.load_data(cust_path, subs_path)

        # Wire Up Strategies via Dependency Injection
        metrics_pipeline = [
            MonthlyMRRMetric(),
            MonthlyChurnMetric(),
            Cohorts()
        ]

        engine = AnalyticsEngine(metrics=metrics_pipeline)
        report = engine.generate_report(df_cust, df_subs)

        # Export computed payload
        with open(out_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Success: Analytics execution report written directly to: {out_path}")

    except Exception as e:
        print(f"Execution Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
