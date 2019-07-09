import pandas as pd
from datetime import datetime


class Inventory:

    def __init__(self, data: pd.DataFrame):
        self.english_cols = [col for col in data.columns if not col.endswith("_fr")]
        self.french_cols = [col for col in data.columns if not col.endswith("_en")]
        english_data = data[self.english_cols]
        french_data = data[self.french_cols]
        english_data.columns = [col.replace("_en", "") for col in self.english_cols]
        french_data.columns = [col.replace("_fr", "") for col in self.french_cols]
        self.english_data = english_data
        self.french_data = french_data
        self.data = data

    @classmethod
    def from_url(cls, url: str):
        data: pd.DataFrame = pd.read_csv(url)
        return cls(data)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        return cls(df)