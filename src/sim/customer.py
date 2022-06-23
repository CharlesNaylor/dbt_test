"""
Data for customers
"""
import datetime
from dataclasses import dataclass, asdict

import pandas as pd
import numpy as np


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

        frame = pd.DataFrame(
            index=pd.date_range(start_date, end_date, freq="B"),
        )
        n_days = frame.shape[0]

        # turnover of 5, for our purposes,
        # means a customer should have an abs val. of cash flows
        # of 5 x the initial investment over the life of the fund
        # this conceals 2 parameters: p(cashflow) and proportion | cashflow
        # (i.e. the frequency and the magnitude of cashflows)
        # Set an average cashflow of 50% of assets, then a p-value such that
        # sum(0.5*binomial draws) gets to the stated turnover
        p_turnover = 2 * turnover / n_days

        n_cashflows = np.random.binomial(n_days, p_turnover)
        cashflow_days = np.random.choice(n_days, n_cashflows, replace=False)

        cashflow_sizes = np.random.standard_normal(size=n_cashflows)
        cashflow_sizes /= turnover * sum(np.abs(cashflow_sizes))

        cashflows = np.zeros(n_days)
        cashflows[cashflow_days] = cashflow_sizes

        frame["Customer"] = self.customer_name
        frame["shareclass"] = self.shareclass_name
        frame["cashflow"] = cashflows

        return frame
