import pandas as pd
from app.metrics.base import BaseMetric

class Cohorts(BaseMetric):
    @property
    def metric_key(self) -> str:
        return "signup_cohorts_3m_retention"

    def calculate(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        if df_cust.empty:
            return {}

        df_cust = df_cust.copy()
        # Safe string mapping conversion for cohort periods
        df_cust['cohort_month'] = df_cust['signup_date'].dt.to_period('M').astype(str)

        cohorts_report = {}
        grouped = df_cust.groupby('cohort_month')

        for cohort_period, group in sorted(grouped):
            cohort_size = len(group)
            active_after_3m = 0

            for _, cust in group.iterrows():
                cust_id = cust['customer_id']

                # FIX: Isolate the raw timestamp scalar value to prevent Series label collisions
                raw_signup_date = pd.Timestamp(cust['signup_date'])
                target_date = raw_signup_date + pd.DateOffset(months=3)

                # Check if the customer has an active subscription at this milestone
                is_retained = df_subs[
                    (df_subs['customer_id'] == cust_id) &
                    (df_subs['start_date'] <= target_date) &
                    (df_subs['end_date'].isna() | (df_subs['end_date'] >= target_date))
                    ]

                if not is_retained.empty:
                    active_after_3m += 1

            retention_rate = round(active_after_3m / cohort_size, 4) if cohort_size > 0 else 0.0

            cohorts_report[str(cohort_period)] = {
                "cohort_size": int(cohort_size),
                "active_after_3_months": int(active_after_3m),
                "retention_rate_3m": float(retention_rate)
            }

        return cohorts_report