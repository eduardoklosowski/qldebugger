import logging

import click

CONFIG_FILENAME = 'qldebugger.toml'


@click.group()
def cli() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:qldebugger:%(message)s')
