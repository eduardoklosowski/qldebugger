import os
import random

import pytest

TEST_SEED_KEY = pytest.StashKey[int]()


def _get_test_seed() -> int:
    try:
        configured_seed = os.environ['PYTEST_TEST_SEED']
        return int(configured_seed)
    except KeyError:
        return random.getrandbits(64)
    except ValueError as e:
        raise pytest.UsageError(f'PYTEST_TEST_SEED must be an integer, but received {configured_seed!r}') from e


def pytest_configure(config: pytest.Config) -> None:
    test_seed = _get_test_seed()
    config.stash[TEST_SEED_KEY] = test_seed
    random.seed(test_seed)


def pytest_report_header(config: pytest.Config) -> str:
    seed = config.stash[TEST_SEED_KEY]
    return f'Test seed: {seed} (reproduce with PYTEST_TEST_SEED={seed})'
