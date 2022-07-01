"""
Orchestrator for the various tables and classes pertaining to fund performance
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AccountingSystem:
    """
    Orchestrator for the various tables and classes pertaining to fund performance
    """

    def __init__(self):
        pass

    @classmethod
    def from_simulated_data(cls, data_path: Path):
        """Generate set of accounts using data simulated by Simulator"""
        data_path = Path(data_path)

        # cashflow.parquet
        # customers.parquet
        # fund_returns.parquet
        # funds.parquet
        # investment.parquet
        # shareclasses.parquet
