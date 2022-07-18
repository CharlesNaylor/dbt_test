"""
Subscriptions and redemptions
"""
import datetime

import numpy as np
import pandas as pd

from src.element import Element


class CashFlow(Element):
    """
    Pct Cashflows for an arbitrary account

    Customers come in and out of investments over time according to the
    customer's turnover preference

    We need to know anything to generate cashflows except for the start and end date,
    and a turnover preference.
    """

    def __init__(
        self,
        cashflow: pd.Series,
        start_date: datetime.date,
        end_date: datetime.date,
        turnover_param: float = None,
        name: str = None,
    ):
        """
        Pct Cashflows for an arbitrary account

        :param cashflow: the actual cashflow values
        :param start_date: the date investment started
        :param end_date: the date records ended
        :param turnover_param: the degree to which the customer churns the account (used for
        simulation) as the simulation's use of this parameter is non-deterministic,
        it won't be calculated when cashflows are provided ahead
        """
        self.cashflow = cashflow
        self.start_date = start_date
        self.end_date = end_date
        self.name = name

        self.turnover_param = turnover_param

    @classmethod
    def from_series(cls, cashflow: pd.Series):
        """Generate from an existing pandas Series object"""
        return cls(
            cashflow=cashflow, start_date=cashflow.index[0], end_date=cashflow.index[-1]
        )

    @classmethod
    def from_parameters(
        cls,
        start_date: datetime.date,
        end_date: datetime.date,
        turnover: float,
        name: str = None,
    ):
        """Generate cashflows according to customer turnover.
        Note no association with fund performance has been included"""

        cashflow = pd.Series(index=pd.date_range(start_date, end_date, freq="B"))
        n_days = cashflow.shape[0]

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

        values = np.zeros(n_days)
        values[cashflow_days] = cashflow_sizes

        cashflow = pd.Series(data=values, index=cashflow.index, name=name)

        return cls(
            cashflow=cashflow,
            start_date=start_date,
            end_date=end_date,
            turnover_param=turnover,
        )

    def to_frame(self):
        """just return the cashflow series"""
        return self.cashflow
