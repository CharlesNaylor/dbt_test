"""
A customer / shareclass pair

TODO:
  - when do cashflows take effect? EoD? T+3?
  - Are expenses subtracted daily? weekly?
    - if less frequently than fund liquidity, how are they pro-rated?
  - are there any expenses not covered by the ratio? e.g. front or back-end loads?
"""
import logging

import pandas as pd

from src.cashflow import CashFlow
from src.customer import Customer
from src.element import Element
from src.fund import FundShareClass

logger = logging.getLogger(__name__)


class Account(Element):
    """
    A customer / shareclass pair
    """

    def __init__(
        self,
        customer: Customer,
        shareclass: FundShareClass,
        cashflows: CashFlow,
        initial_investment: float = 1e6,
    ):
        """
        A customer / fund / shareclass pair
        """
        self.customer = customer
        self.shareclass = shareclass
        self.cashflows = cashflows
        self.initial_investment = initial_investment

    def __str__(self):
        return f"{self.customer}-{self.shareclass}"

    def to_frame(self):
        """Output as a dataframe row"""
        return pd.Series(
            {
                "customer": self.customer.name,
                "fund": self.shareclass.fund.name,
                "shareclass": self.shareclass.name,
                "initial_investment": self.initial_investment,
            }
        )

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
            self.shareclass.name,
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
        for bday, row in values.iterrows():
            values.loc[bday, "init_GAV"] = prev_nav * row["gross_return"]
            values.loc[bday, "GAV"] = values.loc[bday, "init_GAV"] + row["cashflow"]
            values.loc[bday, "expense"] = (
                values.loc[bday, "GAV"] + self.shareclass.expense_ratio
            )
            values.loc[bday, "NAV"] = values.loc[bday, "GAV"] - values.loc[bday, "GAV"]

        return values
