from random import SystemRandom

import pytest

import interactions

random = SystemRandom()

severities = [0, 10, 20, 30, 40, 50]

codes = interactions.LibraryException.errors().keys()

__error = dict(
    _errors=[
        dict(
            code="BASE_TYPE_REQUIRED",
            message="This field is required",
        )
    ]
)
data = dict(
    code=50035,
    errors=dict(
        components={
            "0": dict(
                components={
                    **{str(i): __error for i in range(10)},
                    **{str(i): __error for i in range(10, 74)},
                }
            )
        }
    ),
    message="Invalid Form Body",
)


def test_library_exception_simple():
    for code in codes:
        severity = random.choice(severities)
        if round(random.random()):
            exc = interactions.LibraryException(
                code, message=data["message"], severity=severity, data=data
            )
            assert exc.message == data["message"]
        else:
            exc = interactions.LibraryException(code, severity=severity)
            assert exc.message == interactions.LibraryException.lookup(code)

        assert exc.code == code
        assert exc.severity == severity

        with pytest.raises(interactions.LibraryException):
            raise exc

        try:
            raise exc
        except interactions.LibraryException as e:
            if not e._fmt:
                assert (
                    str(e)
                    == f"\n  Error {e.code} | {e.lookup(e.code)}:\n  {e.message}{'' if e.message.endswith('.') else '.'}\n  Severity {e.severity}."
                )
            else:
                _flag: bool = e.message.lower() in e.lookup(e.code).lower()  # creativity is hard
                assert str(e) == (
                    "\n"
                    f"  Error {e.code} | {e.message if _flag else e.lookup(e.code)}\n"
                    f"  {e._fmt if _flag else e.message}\n"
                    f"  {f'Severity {e.severity}.' if _flag else e._fmt}\n"
                    f"  {'' if _flag else f'Severity {e.severity}.'}"
                )
