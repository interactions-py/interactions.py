import types

import pytest

sentry_sdk = pytest.importorskip("sentry_sdk")

from interactions.ext import sentry as sentry_ext  # noqa: E402


@pytest.fixture
def events():
    captured = []
    sentry_sdk.init(
        "https://key@localhost/1",
        default_integrations=False,
        before_send=lambda event, hint: captured.append(event),  # returning None drops the event
    )
    yield captured
    sentry_sdk.init()


@pytest.mark.asyncio
async def test_error_listener_reports_context(events):
    ctx = types.SimpleNamespace(args=[], kwargs={}, message=None, author=types.SimpleNamespace(id=1, tag="user#1"))
    event = types.SimpleNamespace(source="cmd", ctx=ctx, error=ValueError("boom"))

    await sentry_ext.SentryExtension.__dict__["on_error"].callback(None, event)

    assert events[0]["tags"]["source"] == "cmd"
    assert events[0]["user"]["username"] == "user#1"


def test_task_hook_reports_task_name(events):
    def my_task():
        pass

    task = types.SimpleNamespace(callback=my_task, iteration=3)

    sentry_ext.HookedTask.on_error_sentry_hook(task, ValueError("boom"))

    assert events[0]["tags"] == {"task": "my_task", "iteration": 3}
