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
    *range(10_001, 10_017),
    10_020,
    *range(10_026, 10_034),
    10036,
    10038,
    10049,
    10050,
    10057,
    10059,
    10060,
    10062,
    10063,
    *range(10_065, 10_072),
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

data = {
    "code": 50035,
    "errors": {
        "components": {
            "0": {
                "components": {
                    "0": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "1": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "10": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "11": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "12": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "13": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "14": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "15": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "16": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "17": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "18": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "19": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "2": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "20": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "21": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "22": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "23": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "24": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "25": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "26": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "27": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "28": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "29": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "3": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "30": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "31": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "32": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "33": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "34": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "35": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "36": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "37": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "38": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "39": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "4": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "40": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "41": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "42": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "43": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "44": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "45": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "46": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "47": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "48": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "49": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "5": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "50": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "51": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "52": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "53": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "54": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "55": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "56": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "57": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "58": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "59": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "6": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "60": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "61": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "62": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "63": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "64": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "65": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "66": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "67": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "68": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "69": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "7": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "70": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "71": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "72": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "73": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "8": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                    "9": {
                        "_errors": [
                            {
                                "code": "BASE_TYPE_REQUIRED",
                                "message": "This field is required",
                            }
                        ]
                    },
                }
            }
        }
    },
    "message": "Invalid Form Body",
}


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
