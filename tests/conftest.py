import pytest

import interactions


@pytest.fixture(scope="session")
def fake_client():
    return interactions.Client(
        "ODIzMTQxMTE3ODUxMjA1Njgy.G8pIon.3WZzfl6W-C5HO-E_rAHfCojJKeG6aq3keFvjGw"
    )
    # this token is invalidated


@pytest.fixture(autouse=True)
def clear_commands(fake_client):
    fake_client._commands = []
