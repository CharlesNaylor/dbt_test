"""
Tests for the simulator
"""
import datetime
import pathlib
import tempfile
import unittest

from src.simulator import Simulator


class TestSimulator(unittest.TestCase):
    """tests for simulator"""

    def setUp(self):
        self.simulator_params = dict(
            start_date=datetime.datetime.strptime("2020-01-01", "%Y-%m-%d").date(),
            end_date=datetime.datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
            num_shareclasses=2,
            num_funds=3,
            num_customers=25,
            avg_turnover=1,
        )
        self.expected_files = [
            f"{x}.parquet"
            for x in [
                "funds",
                "shareclasses",
                "fund_returns",
                "customers",
                "accounts",
                "cashflows",
            ]
        ]

    def test_simulate(self):
        """simulate fund accounting data using parameters"""
        sim = Simulator(**self.simulator_params)
        with tempfile.TemporaryDirectory() as outpath:
            sim.simulate(pathlib.Path(outpath), return_params=[0.01, 0.005])
            files = [path.name for path in pathlib.Path(outpath).glob("*.parquet")]
            self.assertEqual(sorted(files), sorted(self.expected_files))
