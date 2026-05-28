import pytest
import pandas as pd
from app.metrics.churn import MonthlyChurnMetric
from app.metrics.cohorts import Cohorts

@pytest.fixture
def base_customer():
    return pd.DataFrame([{
        "customer_id": "C1",
        "signup_date": pd.to_datetime("2024-01-15"),
        "country": "NL"
    }])

def test_churn_no_resubscription(base_customer):
    df_subs = pd.DataFrame([{
        "customer_id": "C1",
        "start_date": pd.to_datetime("2024-01-15"),
        "end_date": pd.to_datetime("2024-03-01"),
        "plan": "pro",
        "monthly_price": 50.0
    }])
    metric = MonthlyChurnMetric()
    res = metric.calculate(base_customer, df_subs)
    assert res == {"2024-03": 1}

def test_resubscription_within_30_days_boundary(base_customer):
    # Ends March 1st, restarts March 31st (exactly 30 days later)
    df_subs = pd.DataFrame([
        {"customer_id": "C1", "start_date": pd.to_datetime("2024-01-15"), "end_date": pd.to_datetime("2024-03-01"), "plan": "pro", "monthly_price": 50.0},
        {"customer_id": "C1", "start_date": pd.to_datetime("2024-03-31"), "end_date": pd.NaT, "plan": "pro", "monthly_price": 50.0}
    ])
    metric = MonthlyChurnMetric()
    res = metric.calculate(base_customer, df_subs)
    assert res == {}  # Not churned because they resubscribed on day 30

def test_resubscription_outside_30_days(base_customer):
    # Ends March 1st, restarts April 2nd (32 days later)
    df_subs = pd.DataFrame([
        {"customer_id": "C1", "start_date": pd.to_datetime("2024-01-15"), "end_date": pd.to_datetime("2024-03-01"), "plan": "pro", "monthly_price": 50.0},
        {"customer_id": "C1", "start_date": pd.to_datetime("2024-04-02"), "end_date": pd.NaT, "plan": "pro", "monthly_price": 50.0}
    ])
    metric = MonthlyChurnMetric()
    res = metric.calculate(base_customer, df_subs)
    assert res == {"2024-03": 1}  # Churned because resubscription took >30 days

def test_cohort_3m_retention_edge_boundary(base_customer):
    # Signup Jan 15 -> Target milestone is Apr 15.
    # Sub 1 ends Apr 14 (Not retained). Sub 2 starts Apr 15 (Retained).
    df_subs = pd.DataFrame([
        {"customer_id": "C1", "start_date": pd.to_datetime("2024-01-15"), "end_date": pd.to_datetime("2024-04-14"), "plan": "pro", "monthly_price": 50.0},
        {"customer_id": "C1", "start_date": pd.to_datetime("2024-04-15"), "end_date": pd.NaT, "plan": "pro", "monthly_price": 50.0}
    ])
    metric = Cohorts()
    res = metric.calculate(base_customer, df_subs)
    assert res["2024-01"]["active_after_3_months"] == 1
    assert res["2024-01"]["retention_rate_3m"] == 1.0
