import logging

from ..config import get_config
from .lambda_ import run_lambda
from .message import delete_messages, receive_message

logger = logging.getLogger(__name__)


def receive_messages_and_run_lambda(*, event_source_mapping_name: str) -> None:
    logger.debug('Execute %r event source mapping...', event_source_mapping_name)
    event_source_mapping = get_config().event_source_mapping[event_source_mapping_name]

    messages = receive_message(
        queue_name=event_source_mapping.queue,
        batch_size=event_source_mapping.batch_size,
        maximum_batching_window=event_source_mapping.maximum_batching_window,
    )
    run_lambda(lambda_name=event_source_mapping.function_name, event=messages)
    delete_messages(queue_name=event_source_mapping.queue, messages=messages)
