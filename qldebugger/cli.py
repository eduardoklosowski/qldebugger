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


# Msg

@cli.group()
def msg() -> None:
    ...


@msg.command('send')
@click.argument('queue_name')
@click.argument('message')
def msg_send(queue_name: str, message: str) -> None:
    load_config(CONFIG_FILENAME)
    actions.message.send_message(queue_name=queue_name, message=message)
