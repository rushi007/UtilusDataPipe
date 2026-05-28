import pandas as pd

from app.metrics.base import BaseMetric


class MonthlyChurnMetric(BaseMetric):
    @property
    def metric_name(self) -> str:
        return 'Monthly_Churn'

    def calculate(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        ended_subs = df_subs[df_subs['end_date'].notna()].copy()
        if ended_subs.empty:
            return {}

        churn_events = []
        for index, row in ended_subs.iterrows():
            cust_id = row['cust_id']
            end_dt = row['end_date']

            # Look for any resubscription within 30-day window
            resubbed = df_subs[
                (df_subs['customer_id'] == cust_id) &
                (df_subs['start_date'] > end_dt) &
                (df_subs['start_date'] <= end_dt + pd.Timedelta(days=30))
            ]

            if resubbed.empty:
                churn_events.append(end_dt.to_period('M'))

        if not churn_events:
            return {}

        # Group churn occurrences by month
        series = pd.Series(churn_events).value_counts().sort_index()
        return {str(m): int(count) for m, count in series.items()}