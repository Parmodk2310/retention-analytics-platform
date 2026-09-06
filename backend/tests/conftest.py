import os

import pytest


@pytest.fixture(scope="session")
def integration_enabled():
    return bool(os.getenv("TEST_DATABASE_URL"))
