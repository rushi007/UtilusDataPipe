from abc import abstractmethod

import pandas as pd


class BaseMetric:
    @property
    @abstractmethod
    def metric_name(self) -> str:
        pass

    @property
    @abstractmethod
    def calculate(self, df_cust: pd.DataFrame, df_subs: pd.DataFrame) -> dict:
        pass