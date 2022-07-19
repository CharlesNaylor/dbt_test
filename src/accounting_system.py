"""
Orchestrator for the various tables and classes pertaining to fund performance
"""
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from src.account import Account
from src.cashflow import CashFlow
from src.customer import Customer
from src.fund import Fund, FundShareClass

logger = logging.getLogger(__name__)


class AccountingSystem:
    """
    Orchestrator for the various tables and classes pertaining to fund performance
    """

    def __init__(
        self,
        data_path: Path,
        cashflows: Dict[str, CashFlow],
        customers: Dict[str, Customer],
        fund_returns: pd.DataFrame,
        funds: Dict[str, Fund],
        accounts: Dict[str, Account],
        shareclasses: Dict[str, FundShareClass],
    ):
        self.data_path = data_path
        self.cashflows = cashflows
        self.customers = customers
        self.fund_returns = fund_returns
        self.funds = funds
        self.accounts = accounts
        self.shareclasses = shareclasses
        self.account_values = None  # holder for calculations of expenses

    @classmethod
    def from_simulated_data(cls, data_path: Path):
        """Generate set of accounts using data simulated by Simulator"""
        logger.info("Generating accounting system from data in %s", data_path)
        data_path = Path(data_path)

        # cashflows.parquet
        cashflow_df = pd.read_parquet(data_path / "cashflows.parquet")
        cashflows = [
            CashFlow.from_series(series) for nm, series in cashflow_df.iteritems()
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
            FundShareClass.from_series(row, funds)
            for i, row in shareclass_df.iterrows()
        ]
        shareclasses = {shareclass.name: shareclass for shareclass in shareclasses}

        # accounts.parquet
        account_df = pd.read_parquet(data_path / "accounts.parquet")
        accounts = {}
        for i, row in account_df.iterrows():
            account = Account(
                customer=customers[row["customer"]],
                shareclass=shareclasses[row["shareclass"]],
                cashflows=cashflows[
                    f"{row['customer']}-{row['fund']}_{row['shareclass']}"
                ],
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

    def returns_for_fund(self, fund_name: str) -> pd.Series:
        """Filter returns to the stated fund_name, return a series"""
        # check if fund name exists in data
        if not fund_name in self.fund_returns.fund.unique():
            raise ValueError(f"{fund_name} does not appear in loaded fund_returns")
        return self.fund_returns[self.fund_returns.fund == fund_name].returns

    def calc_accounts(self):
        """Calculate net returns, expenses, etc. for all accounts"""
        logger.info("Calculating returns, expenses, etc. for all accounts")
        account_values = []
        for account_nm, account in self.accounts.items():
            tmp_vals = account.calculate_values(
                self.returns_for_fund(account.shareclass.fund.name)
            )
            tmp_vals["account"] = account_nm
            tmp_vals["customer"] = account.customer.name
            tmp_vals["fund"] = account.shareclass.fund.name
            tmp_vals["shareclass"] = account.shareclass.name
            account_values.append(tmp_vals)
        return pd.concat(account_values)

    def calc_impact(self, account_values: pd.DataFrame):
        """Calculate the impact between different share classes for all accounts"""
        # TODO: impact shouldn't be separate; it should be calculated as part of
        # calc_accounts. We'd need to know which should be the counterfactual shareclass
        # for each fund
        logger.info("Calculating shareclass impact for all accounts")
        total_expenses = account_values.groupby(
            ["customer", "fund", "shareclass"]
        ).expense.sum()
        impact = total_expenses.groupby(["customer", "fund"]).diff()
        return impact
