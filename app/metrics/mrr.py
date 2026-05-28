import pandas as pd


class MonthlyMRRMetric:
    @property
    def metric_name(self):
        return "MRR"

    def calculate(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        if df_subs.empty:
            return {}

        min_date = df_subs['start_date'].min().to_period('M')
        max_date = max(df_subs['start_date'].max().to_period('M'), df_subs['end_date'].max() if df_subs['end_date'].notna().any() else df_subs['start_date'].max()).to_period('M')
        all_months = pd.period_range(start=min_date, end=max_date, freq='M')

        results = {}
        for month in all_months:
            month_start = month.start_date
            month_end = month.end_date

            is_active = (df_subs['start_date'] <= month_end) & (
                    (df_subs['end_date'].isna()) | (df_subs['end_date'] >= month_start)
            )
            total_mrr = df_subs[is_active]['MRR'].sum()
            results[str(month)] = int(total_mrr)

        return results
