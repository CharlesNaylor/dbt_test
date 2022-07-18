"""
Container for configuration & simulation of the fund accounting system
"""
import datetime
import json
import logging
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from src.account import Account
from src.cashflow import CashFlow
from src.constants import CUSTOMER_NAMES, FUND_NAMES, SHARECLASS_NAMES
from src.customer import Customer
from src.fund import Fund, FundShareClass

logger = logging.getLogger(__name__)


@dataclass
class Simulator:
    """
    Parameters for simulation of funds
    """

    start_date: datetime.date
    end_date: datetime.date
    num_shareclasses: int = 2
    num_funds: int = 1
    num_customers: int = 25
    avg_turnover: float = 1
    expense_ratios: List = field(
        default_factory=lambda: np.linspace(0.95, 1, num=50, endpoint=False)
    )

    @classmethod
    def from_json(cls, json_path: Path):
        """read from config file"""
        with open(Path(json_path), "r") as json_file:
            params = json.load(json_file)

        params["start_date"] = datetime.datetime.strptime(
            params["start_date"], "%Y-%m-%d"
        ).date()
        params["end_date"] = datetime.datetime.strptime(
            params["end_date"], "%Y-%m-%d"
        ).date()
        return cls(**params)

    def to_json(self, json_path: Path):
        """save config to json"""
        params = asdict(self)
        params["start_date"] = params["start_date"].strftime("%Y-%m-%d")
        params["end_date"] = params["end_date"].strftime("%Y-%m-%d")
        with open(Path(json_path), "w") as json_file:
            json.dump(params, fp=json_file)

    def _series_to_frame(self, los: List[pd.Series]):
        """
        convenience function to convert lists of series into a
        dataframe with each element as a row
        """
        return pd.DataFrame(
            [series.to_frame() for series in los],
            columns=los[0].to_frame().index,
        )

    def simulate(self, out_path: Path = None, **kwargs):
        """Simulate fund accounting data using parameters"""
        if out_path is None:
            out_path = Path(f"data/f{datetime.datetime.now():%Y%m%d.%H%M}")

        logger.info("Generating fake data")

        # Funds
        funds = [
            Fund(
                name=fund_name,
                start_date=self.start_date,
                end_date=self.end_date,
                **kwargs,
            )
            for fund_name in np.asarray(FUND_NAMES).take(
                np.random.choice(len(FUND_NAMES), self.num_funds, replace=False)
            )
        ]

        ## Share classes
        shareclasses = []
        for fund in funds:
            for i in range(self.num_shareclasses):
                shareclasses.append(
                    FundShareClass(
                        name=SHARECLASS_NAMES[i],
                        fund=fund,
                        expense_ratio=random.choice(self.expense_ratios),
                    ),
                )

        ## gross performance at fund level
        performances = pd.concat([fund.simulate_performance() for fund in funds])

        # Customers
        ## name, etc.
        customers = {
            f"{name}_{i}": Customer(name=f"{name}_{i}", turnover=turnover)
            for i, (name, turnover) in enumerate(
                zip(
                    np.asarray(CUSTOMER_NAMES).take(
                        np.random.choice(len(CUSTOMER_NAMES), self.num_customers)
                    ),
                    np.abs(
                        np.random.normal(self.avg_turnover, size=self.num_customers)
                    ),
                )
            )
        }

        ## investments
        # make one account per customer per shareclass
        # also make cash flows
        accounts = []
        cashflows = []
        for customer in customers.values():
            for shareclass in shareclasses:
                cashflows.append(
                    CashFlow.from_parameters(
                        start_date=self.start_date,
                        end_date=self.end_date,
                        turnover=customer.turnover,
                        name=f"{customer}-{shareclass}",
                    )
                )
                accounts.append(
                    Account(
                        customer=customer,
                        shareclass=shareclass,
                        cashflows=cashflows[-1],
                        initial_investment=np.random.randint(10, 1000) * 1000,
                    )
                )

        # dump to parquet
        logger.info("Writing data to %s", out_path)
        out_path.mkdir(parents=True, exist_ok=True)
        self._series_to_frame(funds).to_parquet(out_path / "funds.parquet")
        self._series_to_frame(shareclasses).to_parquet(
            out_path / "shareclasses.parquet"
        )
        performances.to_parquet(out_path / "fund_returns.parquet")
        self._series_to_frame(list(customers.values())).to_parquet(
            out_path / "customers.parquet"
        )
        self._series_to_frame(accounts).to_parquet(out_path / "accounts.parquet")
        self._series_to_frame(cashflows).T.to_parquet(out_path / "cashflows.parquet")
