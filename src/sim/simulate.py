"""
Container for configuration & simulation of the fund accounting system
"""
import datetime
import json
import logging
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from src.sim.constants import FUND_NAMES, SHARECLASS_NAMES
from src.sim.fund import Fund, FundShareClass

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
    mgmt_fees: List[float] = [0.01, 0.005, 0]
    perf_fees: List[float] = [0, 0.1, 0.2]

    @classmethod
    def from_json(cls, json_path: Path):
        """read from config file"""
        with open(Path(json_path), "r") as json_file:
            params = json.load(json_file)

    def to_json(self, json_path: Path):
        """save config to json"""
        with open(Path(json_path), "w") as json_file:
            json.dump(asdict(self), fp=json_file)

    def _series_to_frame(self, los: List[pd.Series]):
        """
        convenience function to convert lists of series into a
        dataframe with each element as a row
        """
        return pd.DataFrame(
            [series.to_frame() for series in los],
            columns=los[0].index,
        )

    def simulate(self, out_path: Path = None):
        """Simulate fund accounting data using parameters"""
        if out_path is None:
            out_path = Path(f"data/f{datetime.datetime.now():%Y%m%d%H%M}")

        logger.info("Generating fake data")
        # Funds
        funds = [
            Fund(
                name=fund_name,
                start_date=self.start_date,
                end_date=self.end_date,
                return_scale=return_scale,
            )
            for fund_name in np.take(
                np.random.choice(len(FUND_NAMES), self.num_funds, replace=False),
                FUND_NAMES,
            )
        ]

        ## Share classes
        share_classes = []
        for fund in funds:
            for i in range(num_shareclasses):
                share_classes.append(
                    FundShareClass(
                        name=SHARECLASS_NAMES[i],
                        fund=fund.name,
                        mgmt_fee=random.choice(self.mgmt_fees),
                        perf_fee=random.choice(self.perf_fees),
                    ),
                )

        ## gross performance at fund level
        performances = pd.concat([fund.simulate_performance() for fund in funds])

        ## fee accrual

        # Customers
        ## name, etc.
        customers = [
            Customer(name=f"{name}_{i}", turnover=turnover)
            for i, (name, turnover) in enumerate(
                zip(
                    np.take(np.random.choice(len(CUSTOMER_NAMES), CUSTOMER_NAMES)),
                    np.abs(
                        np.random.normal(self.avg_turnover, shape=self.num_customers)
                    ),
                )
            )
        ]

        ## investments
        # just make one shareclass-fund per customer
        investments = [
            Investment(customer.name, random.choice(share_classes))
            for customer in customers
        ]

        ## cash flows
        cashflows = pd.concat(
            [
                investment.simulate_cashflows(
                    start_date=self.start_date,
                    end_date=self.end_date,
                )
                for investment in investments
            ]
        )

        # dump to parquet
        logger.info("Writing data to %s", out_path)
        out_path.mkdir(parents=True, exist_ok=True)
        self._series_to_frame(funds).to_parquet(out_path / "funds.parquet")
        self._series_to_frame(share_classes).to_parquet(
            out_path / "shareclasses.parquet"
        )
        performances.to_parquet(out_path / "fund_returns.parquet")
        self._series_to_frame(customers).to_parquet(out_path / "customers.parquet")
        self._series_to_frame(investment).to_parquet(out_path / "investment.parquet")
        cashflows.to_parquet(out_path / "cashflow.parquet")
