import pandas as pd
from typing import List
from app.metrics.base import BaseMetric

class AnalyticsEngine:
    def __init__(self, metrics: List[BaseMetric]):
        self.metrics = metrics

    def generate_report(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        report = {}
        for metric in self.metrics:
            report[metric.metric_key] = metric.calculate(df_cust, df_subs)
        return report
