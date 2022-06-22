"""
Data for customers
"""
import datetime
from dataclasses import dataclass, asdict
from typing import Callable, List

import pandas as pd


@dataclass
class Customer:
    """
    An investor in a fund share class

    :param turnover: what rough % of assets does this customer turnover per year?
    """

    name: str
    turnover: float

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(asdict(self))


@dataclass
class Investment:
    """
    A customer / shareclass pair

    Customers come in and out of investments over time according to the
    customer's turnover preference
    """

    customer_name: str
    shareclass_name: str

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(asdict(self))

    def simulate_cashflows(
        self, start_date: datetime.date, end_date: datetime.date, turnover: float
    ) -> pd.Series:
        """Generate cashflows according to customer turnover.
        Note no association with fund performance has been included"""

        df = pd.DataFrame(
            index=pd.DateTimeIndex(start_date, end_date, freq="BD"),
        )
        n_days = df.shape[0]

        initial_investment = np.random.randint(1e2, 1e7)

        # turnover of 5, for our purposes,
        # means a customer should have an abs val. of cash flows
        # of 5 x the initial investment over the life of the fund
        # this conceals 2 parameters: p(cashflow) and proportion | cashflow
        # (i.e. the frequency and the magnitude of cashflows)
        # Set an average cashflow of 50% of assets, then a p-value such that
        # sum(0.5*binomial draws) gets to the stated turnover
        p_turnover = 2 * turnover / n_days

        n_cashflows = np.random.binomial(n_days, p_turnover)
        cashflow_days = np.random.choose(n_days, n_cashflows, replace=False)

        cashflow_sizes = np.random.standard_normal(shape=n_cashflows)
        cashflow_sizes /= turnover * sum(np.abs(cashflow_sizes))

        cashflows = np.zeros(n_days)
        cashflows[cashflow_days] = cashflow_sizes

        df["Customer"] = self.customer_name
        df["shareclass"] = self.shareclass_name
        df["cashflow"] = cashflows

        return df
