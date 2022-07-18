"""
Orchestrator for the various tables and classes pertaining to fund performance
"""
import logging
from pathlib import Path
from typing import Dict, List

from src.cashflow import Cashflow
from src.customer import Customer
from src.fund import Fund, FundShareClasee

logger = logging.getLogger(__name__)


class AccountingSystem:
    """
    Orchestrator for the various tables and classes pertaining to fund performance
    """

    def __init__(
        self,
        data_path: Path,
        cashflows: Dict[str, Cashflow],
        customers: Dict[str, Customer],
        fund_returns: pd.DataFrame,
        funds: Dict[str, Fund],
        accounts: Dict[str, Account],
        shareclasses: Dict[str, ShareClass],
    ):
        self.data_path = data_path
        self.cashflows = cashflows
        self.customers = customers
        self.fund_returns = fund_returns
        self.funds = funds
        self.accounts = accounts
        self.shareclasses = shareclasses

    @classmethod
    def from_simulated_data(cls, data_path: Path):
        """Generate set of accounts using data simulated by Simulator"""
        data_path = Path(data_path)

        # cashflows.parquet
        cashflow_df = pd.read_parquet(data_path / "cashflows.parquet")
        cashflows = [
            Cashflow.from_series(series) for nm, series in cashflow_df.iteritems()
        ]
        cashflows = {cf.name: cf for cf in cashflows}

        # customers.parquet
        customer_df = pd.read_parquet(data_path / "customers.parquet")
        customers = [Customer.from_series(row) for i, row in customer_df.iterrows()]
        customers = {cus.name: cus for cus in customers}

        # fund_returns.parquet
        fund_returns = pd.read_parquet(data_path / "fund_returns.parquet")

        # funds.parquet
        fund_df = pd.read_parquet(data_path / "funds.parquet")
        funds = [Fund.from_series(row) for i, row in fund_df.iterrows()]
        funds = {fund.name: fund for fund in funds}

        # shareclasses.parquet
        shareclass_df = pd.read_parquet(data_path / "shareclasses.parquet")
        shareclasses = [
            Shareclass.from_series(row) for i, row in shareclass_df.iterrows()
        ]
        shareclasses = {shareclass.name: shareclass for shareclass in shareclasses}

        # accounts.parquet
        account_df = pd.read_parquet(data_path / "accounts.parquet")
        accounts = {}
        for i, row in account_df.iterrows():
            account = Account(
                customer=customers[row["customer"]],
                shareclass=shareclasses[row["shareclass"]],
                cashflows=cashflows[row["cashflow"]],
                initial_investment=row["initial_investment"],
            )
            accounts[account.name] = account

        return cls(
            data_path=data_path,
            cashflows=cashflows,
            customers=customers,
            fund_returns=fund_returns,
            funds=funds,
            accounts=accounts,
            shareclasses=shareclasses,
        )
