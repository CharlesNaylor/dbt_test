"""
Datastore + simulation code for funds
"""
from dataclasses import dataclass, asdict
from typing import Callable, List

import pandas as pd

@dataclass
class Fund:
    """
    An investable fund

    :param return_params: parameters for the returns generator
    """

    name: str
    start_date: datetime.date
    end_date: datetime.date
    return_params: List[float] = [0.01, 0.1]
    return_generator: Callable = np.random.normal

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(asdict(self))

    def simulate_performance(self) -> pd.DataFrame:
        """generate gross returns according to provided parameters"""
        df = pd.DataFrame(index = pd.DateTimeIndex(start_date, end_date, freq="BD"))
        df['fund'] = self.name
        df['returns'] = self.return_generator(*self.return_params, size=df.shape)
        return df


@dataclass
class FundShareClass:
    """A shareclass of an investable fund"""

    name: str,
    fund_name: str, # fk to Fund name
    mgmt_fee: float,
    perf_fee: float,

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(asdict(self))

    def __repr__(self):
        """NB. we are not enforcing uniqueness anywhere"""
        return f"{self.fund_name}_{self.name}"

