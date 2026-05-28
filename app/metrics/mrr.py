import pandas as pd

from app.metrics.base import BaseMetric


class MonthlyMRRMetric(BaseMetric):
    @property
    def metric_key(self) -> str:
        return "monthly_mrr"

    def calculate(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        if df_subs.empty:
            return {}

        # Determine the dynamic calendar range based on active dates
        min_date = df_subs['start_date'].min().to_period('M')

        max_sub_date = df_subs['start_date'].max()
        if df_subs['end_date'].notna().any():
            max_sub_date = max(max_sub_date, df_subs['end_date'].max())
        max_date = max_sub_date.to_period('M')

        all_months = pd.period_range(start=min_date, end=max_date, freq='M')

        results = {}
        for month in all_months:
            # Extract clean, comparable Timestamp objects for boundaries
            month_start = month.start_time
            month_end = month.end_time

            # Match condition: overlap with the calendar month timeline
            is_active = (df_subs['start_date'] <= month_end) & (
                    df_subs['end_date'].isna() | (df_subs['end_date'] >= month_start)
            )

            total_mrr = df_subs[is_active]['monthly_price'].sum()
            results[str(month)] = int(total_mrr)

        return results