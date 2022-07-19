"""
Data for customers
"""
from dataclasses import dataclass, asdict

import pandas as pd


@dataclass
class Customer:
    """
    An investor in a fund share class

    :param turnover: what rough % of assets does this customer turnover per year?
    """

    name: str
    turnover: float

    @classmethod
    def from_series(cls, series):
        """reconstitute from the parquet"""
        return cls(**series.to_dict())

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(asdict(self))

    def __str__(self):
        return self.name
