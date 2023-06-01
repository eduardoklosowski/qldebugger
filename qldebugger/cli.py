import logging
from pathlib import Path

import click

from . import actions
from .config import load_config

CONFIG_FILENAME = Path('qldebugger.toml')


@click.group()
def cli() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:qldebugger:%(message)s')


@cli.command()
def init() -> None:
    config = '''[aws]
profile = ""
access_key_id = "secret"
secret_access_key = "secret"
session_token = ""
region = "us-east-1"
endpoint_url = "http://localhost:4566/"

[queues]
myqueue = {}

[lambdas]
print = {handler = "qldebugger.example.lambdas.print_messages"}
[lambdas.fail]
handler = "qldebugger.example.lambdas.exec_fail"
[lambdas.fail.environment]
VARIABLE = "VALUE"

[event_source_mapping]
a = {queue = "myqueue", function_name = "print"}
b = {queue = "myqueue", function_name = "fail", batch_size = 1, maximum_batching_window = 20}
'''
    if CONFIG_FILENAME.exists():
        click.echo('Configuration file already exists')
        return
    with CONFIG_FILENAME.open('w') as fp:
        fp.write(config)
    click.echo('Configuration file created')


@cli.command()
@click.argument('event_source_mapping_name')
def run(event_source_mapping_name: str) -> None:
    load_config(CONFIG_FILENAME)
    actions.event_source_mapping.receive_messages_and_run_lambda(event_source_mapping_name=event_source_mapping_name)


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
