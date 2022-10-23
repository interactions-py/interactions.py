from random import SystemRandom

import pytest

import interactions

random = SystemRandom()

severities = [0, 10, 20, 30, 40, 50]

codes = (
    *range(15),
    400,
    401,
    *range(403, 406),
    429,
    502,
    *range(4000, 4015),
    *range(10001, 10017),
    10020,
    *range(10026, 10034),
    10036,
    10038,
    10049,
    10050,
    10057,
    10059,
    10060,
    10062,
    10063,
    *range(10065, 10072),
    10087,
    20001,
    20002,
    20009,
    20012,
    20016,
    20018,
    20022,
    20024,
    20028,
    20029,
    20031,
    20035,
    *range(30_001, 30_006),
    30007,
    30008,
    30010,
    30013,
    30015,
    30016,
    30018,
    30019,
    *range(30030, 30036),
    *range(30037, 30041),
    30042,
    30046,
    30047,
    30048,
    30052,
    *range(40001, 40008),
    40012,
    40032,
    40033,
    40041,
    40043,
    40060,
    40061,
    *range(50001, 50018),
    *range(50019, 50022),
    *range(50024, 50029),
    *range(50033, 50037),
    50041,
    50045,
    50046,
    50054,
    50055,
    50068,
    50070,
    50074,
    50080,
    50081,
    *range(50083, 50087),
    50095,
    50097,
    50101,
    50109,
    50132,
    50138,
    50146,
    50600,
    60003,
    80004,
    90001,
    110001,
    130000,
    150006,
    160002,
    *range(160004, 160008),
    *range(170001, 170008),
    180000,
    180002,
    200000,
    200001,
    220003,
)

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
