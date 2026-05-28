from typing import Tuple

import logging
import pandas as pd
from pydantic import ValidationError

from app.models import CustomerModel, SubscriptionModel


logger = logging.getLogger("DataPipe")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class DataParser:

    @classmethod
    def load_data(cls, cust_path:str, subs_path:str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_cust_raw, df_subs_raw = cls._read_and_strip_csvs(cust_path, subs_path)

        df_cust_clean = cls._clean_customers(df_cust_raw)
        df_subs_clean = cls._clean_subscriptions(df_subs_raw)

        cls._lint_cross_references(df_cust_clean, df_subs_clean)

        return df_cust_clean, df_subs_clean

    @staticmethod
    def _read_and_strip_csvs(cust_path: str, subs_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Reads CSV files and trims whitespaces from text inputs."""
        try:
            df_cust = pd.read_csv(cust_path).map(lambda x: x.strip() if isinstance(x, str) else x)
            df_subs = pd.read_csv(subs_path).map(lambda x: x.strip() if isinstance(x, str) else x)
            df_cust.columns = df_cust.columns.str.strip()
            df_subs.columns = df_subs.columns.str.strip()
            return df_cust, df_subs
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV files: {str(e)}")

    @staticmethod
    def _clean_customers(df: pd.DataFrame) -> pd.DataFrame:
        """Validates and filters the customer data profile."""
        # Malformed dates seamlessly morph into NaT markers via vectorized arrays
        df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')

        bad_rows = df[df['customer_id'].isna() | df['signup_date'].isna()]
        if not bad_rows.empty:
            logger.warning(f"Dropped {len(bad_rows)} invalid customer records (missing IDs/bad dates).")

        return df.dropna(subset=['customer_id', 'signup_date']).copy()

    @staticmethod
    def _clean_subscriptions(df: pd.DataFrame) -> pd.DataFrame:
        """Validates and filters subscription transactional history records."""
        # Convert non-digit rows (like "thirty") to NaN, default to -1, cast to clean integers
        df['monthly_price'] = pd.to_numeric(df['monthly_price'], errors='coerce').fillna(-1).astype(int)
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')

        # Matrix alignment masks
        valid_id = df['customer_id'].notna() & (df['customer_id'] != '')
        valid_start = df['start_date'].notna()
        valid_price = df['monthly_price'] >= 0
        valid_timeline = df['end_date'].isna() | (df['end_date'] >= df['start_date'])

        # Aggregate logical operations concurrently
        valid_mask = valid_id & valid_start & valid_price & valid_timeline

        bad_rows = df[~valid_mask]
        if not bad_rows.empty:
            logger.warning(f"Dropped {len(bad_rows)} invalid subscription records (bad prices/chronology).")

        return df[valid_mask].copy()

    @staticmethod
    def _lint_cross_references(df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> None:
        """Checks for missing foreign key relationships between datasets."""
        if df_cust.empty or df_subs.empty:
            return

        known_ids = set(df_cust['customer_id'])
        unknown_subs = df_subs[~df_subs['customer_id'].isin(known_ids)]

        if not unknown_subs.empty:
            unique_misses = list(unknown_subs['customer_id'].unique())
            logger.warning(f"Data Quality Issue: Found subscriptions with unknown customer IDs: {unique_misses}")