from typing import Tuple

import logging
import pandas as pd
from pydantic import ValidationError

from app.models import CustomerModel, SubscriptionModel


logger = logging.getLogger("DataPipe")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class DataParser:
    @staticmethod
    def load_data(customer_path: str, subscription_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            df_subscription = pd.read_csv(subscription_path)
            df_customer = pd.read_csv(customer_path)
        except Exception as e:
            raise RuntimeError(f"Error loading data from {customer_path} and {subscription_path}: {e}")

        # check required structure
        req_cust = {"customer_id", "signup_date", "country"}
        req_sub = {"customer_id", "start_date", "end_date", "plan", "monthly_price"}

        if not req_cust.issubset(df_customer.columns):
            raise ValueError(f"Missing columns in customers CSV. expected {req_cust}")

        if not req_sub.issubset(df_subscription.columns):
            raise ValueError(f"Missing columns in subscriptions CSV. expected {req_sub}")

        # Validate rows
        validated_cust = []
        for idx, row in df_customer.iterrows():
            try:
                validated_cust.append(CustomerModel(**row.to_dict()).model_dump())
            except ValidationError as e:
                raise ValueError(f"Error parsing row {idx} in customers CSV: {e}")

        validated_sub = []
        for idx, row in df_subscription.iterrows():
            row_dict = row.to_dict()
            if pd.isna(row_dict.get("end_date")):
                row_dict["end_date"] = None
            try:
                validated_sub.append(SubscriptionModel(**row_dict).model_dump())
            except ValidationError as e:
                raise ValueError(f"Error parsing row {idx} in subscriptions CSV: {e}")

        df_customer_clean =  pd.DataFrame(validated_cust)
        df_subscription_clean = pd.DataFrame(validated_sub)

        known_cust_ids = set(df_customer_clean['customer_id'])
        unknown_subs = df_subscription_clean[~df_subscription_clean['customer_id'].isin(known_cust_ids)]
        if not unknown_subs.empty:
            unique_unknowns = unknown_subs['customer_id'].unique()
            logger.warning(f"Data Quality Issue: Found subscriptions with unknown customer_ids: {list(unique_unknowns)}")

        # Convert back to native Pandas datetime types for calculation layers
        df_subscription_clean['signup_date'] = pd.to_datetime(df_subscription_clean['signup_date'])
        df_subscription_clean['start_date'] = pd.to_datetime(df_subscription_clean['start_date'])
        df_subscription_clean['end_date'] = pd.to_datetime(df_subscription_clean['end_date'])

        return df_customer_clean, df_subscription_clean