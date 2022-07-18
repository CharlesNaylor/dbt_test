"""
Datastore + simulation code for funds
"""
import datetime
from dataclasses import asdict, dataclass, field
from typing import Callable, List

import pandas as pd
import numpy as np

from src.element import Element


@dataclass
class Fund(Element):
    """
    An investable fund

    :param return_params: parameters for the returns generator
    """

    name: str
    start_date: datetime.date
    end_date: datetime.date
    return_params: List[float] = field(default_factory=lambda: [0.01, 0.005])
    return_generator: Callable = np.random.normal

    @classmethod
    def from_series(cls, series: pd.Series):
        """reconstitute from a pandas series"""
        series["return_generator"] = cls.generator_for_string(
            series["return_generator"]
        )
        return Fund(**series.to_dict())

    @staticmethod
    def generator_for_string(generator: str) -> Callable:
        """get a proper generator from a string (currently only supports normal)"""
        OPTIONS = {"normal": np.random.normal}
        return OPTIONS[generator]

    def to_frame(self):
        """Output as a dataframe row"""
        out = asdict(self)
        # don't serialize the method
        out["return_generator"] = out["return_generator"].__name__
        return pd.Series(out)

    def simulate_performance(self) -> pd.DataFrame:
        """generate gross returns according to provided parameters"""
        frame = pd.DataFrame(
            index=pd.date_range(self.start_date, self.end_date, freq="B")
        )
        frame["fund"] = self.name
        frame["returns"] = self.return_generator(*self.return_params, size=frame.shape)
        return frame


@dataclass
class FundShareClass(Element):
    """A shareclass of an investable fund"""

    name: str
    fund: Fund  # fk to Fund name
    expense_ratio: float

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(
            dict(name=self.name, fund=self.fund.name, expense_ratio=self.expense_ratio)
        )

    def __repr__(self):
        """NB. we are not enforcing uniqueness anywhere"""
        return f"{self.fund.name}_{self.name}"
