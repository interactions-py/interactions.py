from random import SystemRandom

import pytest

import interactions

random = SystemRandom()

severities = [0, 10, 20, 30, 40, 50]

codes = (
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    400,
    401,
    403,
    404,
    405,
    429,
    502,
    4000,
    4001,
    4002,
    4003,
    4004,
    4005,
    4007,
    4008,
    4009,
    4010,
    4011,
    4012,
    4013,
    4014,
    10001,
    10002,
    10003,
    10004,
    10005,
    10006,
    10007,
    10008,
    10009,
    10010,
    10011,
    10012,
    10013,
    10014,
    10015,
    10016,
    10020,
    10026,
    10027,
    10028,
    10029,
    10030,
    10031,
    10032,
    10033,
    10036,
    10038,
    10049,
    10050,
    10057,
    10059,
    10060,
    10062,
    10063,
    10065,
    10066,
    10067,
    10068,
    10069,
    10070,
    10071,
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
    30001,
    30002,
    30003,
    30004,
    30005,
    30007,
    30008,
    30010,
    30013,
    30015,
    30016,
    30018,
    30019,
    30030,
    30031,
    30032,
    30033,
    30034,
    30035,
    30037,
    30038,
    30039,
    30040,
    30042,
    30046,
    30047,
    30048,
    30052,
    40001,
    40002,
    40003,
    40004,
    40005,
    40006,
    40007,
    40012,
    40032,
    40033,
    40041,
    40043,
    40060,
    40061,
    50001,
    50002,
    50003,
    50004,
    50005,
    50006,
    50007,
    50008,
    50009,
    50010,
    50011,
    50012,
    50013,
    50014,
    50015,
    50016,
    50017,
    50019,
    50020,
    50021,
    50024,
    50025,
    50026,
    50027,
    50028,
    50033,
    50034,
    50035,
    50036,
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
    50083,
    50084,
    50085,
    50086,
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
    160004,
    160005,
    160006,
    160007,
    170001,
    170002,
    170003,
    170004,
    170005,
    170006,
    170007,
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
