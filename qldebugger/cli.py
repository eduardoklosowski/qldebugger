import logging

import click

from . import actions
from .config import load_config

CONFIG_FILENAME = 'qldebugger.toml'


@click.group()
def cli() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:qldebugger:%(message)s')


# Infra

@cli.group()
def infra() -> None:
    ...


@infra.command('create-queues')
def infra_create_queues() -> None:
    load_config(CONFIG_FILENAME)
    actions.infra.create_queues()
