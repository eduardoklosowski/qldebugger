from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


def print_messages(event: 'ReceiveMessageResultTypeDef', context: None) -> None:
    for message in event['Messages']:
        print(message['Body'])
    print(f'Total: {len(event["Messages"])} messages')


def exec_fail(event: 'ReceiveMessageResultTypeDef', context: None) -> None:
    raise Exception('Lambda execution fail')
