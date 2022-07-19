"""
CLI for fund accounting simulator + dbt
"""
import datetime
import logging
from pathlib import Path

import click

from src import AccountingSystem, Simulator

logging.basicConfig(format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    """base CLI group"""
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@cli.command()
@click.option(
    "--config_path",
    required=True,
    type=str,
    help="Path to serialized data generation config",
)
@click.option(
    "--return_mean",
    default=0.01,
    type=float,
    help="mean daily return",
)
@click.option("--return_scale", default=0.005, type=float, help="sigma of daily return")
def generate_data(config_path: str, return_mean: float, return_scale: float):
    """Simulate fund accounting data for use in dbt"""
    sim = Simulator.from_json(config_path)

    out_path = Path(f"data/{datetime.datetime.now():%Y%m%d.%H%M}")
    sim.simulate(out_path, return_params=[return_mean, return_scale])


@cli.command()
@click.option(
    "--data_path",
    required=True,
    type=str,
    help="Path to simulated data",
)
@click.option(
    "--out_path",
    default=None,
    type=str,
    help="Path to which to output results",
)
def calculate_impact(data_path: str, out_path: str):
    """Calculate difference between share class expenses using specified data"""
    account_system = AccountingSystem.from_simulated_data(data_path)
    account_values = account_system.calc_accounts()
    impact = account_system.calc_impact(account_values)

    if out_path is None:
        out_path = data_path
    logger.info("Outputting impact and account values to %s", out_path)
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)
    account_values.to_csv(out_path / "account_values.csv")
    impact.to_csv(out_path / "impact.csv")


if __name__ == "__main__":
    cli()
    logger.info("Done")
