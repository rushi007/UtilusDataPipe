import pandas as pd
from app.metrics.base import BaseMetric

class MonthlyChurnMetric(BaseMetric):
    @property
    def metric_key(self) -> str:
        return "monthly_churn_count"

    def calculate(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        # Filter for rows that have historical termination dates
        ended_subs = df_subs[df_subs['end_date'].notna()].copy()
        if ended_subs.empty:
            return {}

        churn_events = []
        for _, end_row in ended_subs.iterrows():
            cust_id = end_row['customer_id']
            end_dt = end_row['end_date']  # This is a clean Pandas Timestamp

            # Query for an explicit reactivation within 30 days
            resubbed = df_subs[
                (df_subs['customer_id'] == cust_id) &
                (df_subs['start_date'] > end_dt) &
                (df_subs['start_date'] <= end_dt + pd.Timedelta(days=30))
                ]

            if resubbed.empty:
                # Convert to string month representation safely at the end
                churn_events.append(str(end_dt.to_period('M')))

        if not churn_events:
            return {}

        # Group, aggregate, and return clear metrics
        series = pd.Series(churn_events).value_counts().sort_index()
        return {str(m): int(count) for m, count in series.items()}