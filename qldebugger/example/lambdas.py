from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aws_lambda_typing.events import SQSEvent


def print_messages(event: 'SQSEvent', context: None) -> None:
    for message in event['Records']:
        print(message['body'])
    print(f'Total: {len(event["Records"])} messages')


class LambdaCustomError(Exception):
    def __str__(self) -> str:
        return 'Lambda execution fail'


def exec_fail(event: 'SQSEvent', context: None) -> None:
    raise LambdaCustomError
