"""
A customer / shareclass pair

TODO:
  - when do cashflows take effect? EoD? T+3?
  - Are expenses subtracted daily? weekly?
    - if less frequently than fund liquidity, how are they pro-rated?
  - are there any expenses not covered by the ratio? e.g. front or back-end loads?
"""
import datetime
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Account:
    """
    A customer / shareclass pair
    """

    def __init__(
        self,
        customer: Customer,
        share_class: FundShareClass,
        cashflows: CashFlow,
        initial_investment: float = 1e6,
    ):
        """
        A customer / fund / shareclass pair
        """
        self.customer = Customer
        self.share_class = share_class
        self.cashflows = cashflows
        self.initial_investment = initial_investment

    def calculate_values(self, gross_returns: pd.Series) -> pd.DataFrame:
        """
        Given fund gross returns, and share class expenses, calculate personal net returns

        1. Add initial subscription
        2. for each trading day:
          a. apply gross return to account value
          b. apply subscriptions / redemptions
          c. calculate expenses
          d. subtract day's expenses from account value
        """
        logger.info(
            "Calculating asset values for %s, %s",
            self.customer.name,
            self.share_class.name,
        )

        values = pd.DataFrame(
            {"gross_return": gross_returns, "cashflow": self.cashflows}
        )
        values = pd.merge(
            values,
            pd.DataFrame(
                index=values.index, columns=["init_GAV", "GAV", "expense", "NAV"]
            ),
        )

        # TODO: do we have to iterate? I think so.
        prev_nav = self.initial_investment
        for t, row in values.iterrows():
            values.loc[t, "init_GAV"] = prev_nav * row["gross_return"]
            values.loc[t, "GAV"] = values.loc[t, "init_GAV"] + row["cashflow"]
            values.loc[t, "expense"] = (
                values.loc[t, "GAV"] + self.share_class.expense_ratio
            )
            values.loc[t, "NAV"] = values.loc[t, "GAV"] - values.loc[t, "GAV"]

        return values
