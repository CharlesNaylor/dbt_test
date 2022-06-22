"""
CLI for fund accounting simulator + dbt
"""
import datetime
import json
import logging
from pathlib import Path

import click
import numpy as np

logging.basicConfig(format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
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
def generate_data(
    config_path: str, output_pattern: str = "data/{name}_{version}_{timestamp}.json"
):
    pass


if __name__ == "__main__":
    cli()
    logger.info("Done")
