"""
CLI for fund accounting simulator + dbt
"""
import datetime
import logging
from pathlib import Path

import click

from src.sim import Simulator

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


if __name__ == "__main__":
    cli()
    logger.info("Done")
