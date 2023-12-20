import argparse

import requests_mock

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2

METGET_CREDIT_RESPONSE_JSON = {
    "statusCode": 200,
    "body": {"credit_limit": 0.0, "credits_used": 13707.9168, "credit_balance": 0.0},
}

METGET_CREDIT_RESPONSE_TEXT = (
    "+--------------+--------------+----------------+\n"
    "| Credit Limit | Credits Used | Credit Balance |\n"
    "+--------------+--------------+----------------+\n"
    "|  Unlimited   |  13707.9168  |   Unlimited    |\n"
    "+--------------+--------------+----------------+\n"
)

METGET_FORMATTED_CREDIT_RESPONSE_JSON = {
    "credit_limit": "Unlimited",
    "credits_used": 13707.9168,
    "credit_balance": "Unlimited",
}


def test_credits(capfd) -> None:
    """
    Tests the credits data
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    import json

    from metget.metget_credits import metget_credits

    args = argparse.Namespace()
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION
    args.format = "json"

    url = METGET_DMY_ENDPOINT + "/credits"
    with requests_mock.Mocker() as m:
        m.get(
            url,
            headers={"x-api-key": METGET_DMY_APIKEY},
            json=METGET_CREDIT_RESPONSE_JSON,
        )
        metget_credits(args)
        out, err = capfd.readouterr()
        out = out.replace("'", '"')
        assert json.loads(out) == METGET_FORMATTED_CREDIT_RESPONSE_JSON

        args.format = "pretty"
        metget_credits(args)
        out, err = capfd.readouterr()
        assert out == METGET_CREDIT_RESPONSE_TEXT
