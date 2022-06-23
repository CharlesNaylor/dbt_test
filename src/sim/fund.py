"""
Datastore + simulation code for funds
"""
import datetime
from dataclasses import asdict, dataclass, field
from typing import Callable, List

import pandas as pd
import numpy as np


@dataclass
class Fund:
    """
    An investable fund

    :param return_params: parameters for the returns generator
    """

    name: str
    start_date: datetime.date
    end_date: datetime.date
    return_params: List[float] = field(default_factory=lambda: [0.01, 0.005])
    return_generator: Callable = np.random.normal

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
class FundShareClass:
    """A shareclass of an investable fund"""

    name: str
    fund_name: str  # fk to Fund name
    mgmt_fee: float
    perf_fee: float

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(asdict(self))

    def __repr__(self):
        """NB. we are not enforcing uniqueness anywhere"""
        return f"{self.fund_name}_{self.name}"
