import requests_mock
import argparse
from urllib.parse import urlencode
from metget_client.metget_track import MetGetTrack
from .track_json import *

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2


def test_best_track(capfd) -> None:
    """
    Tests the best track data
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    import json
    import os

    args = argparse.Namespace()
    args.type = "besttrack"
    args.storm = 9
    args.year = 2022
    args.basin = "al"

    # ...Test using the environment variables
    os.environ["METGET_ENDPOINT"] = METGET_DMY_ENDPOINT
    os.environ["METGET_API_KEY"] = METGET_DMY_APIKEY
    os.environ["METGET_API_VERSION"] = str(METGET_API_VERSION)
    args.endpoint = None
    args.apikey = None
    args.api_version = None

    with requests_mock.Mocker() as m:
        url = (
            METGET_DMY_ENDPOINT
            + "/stormtrack?"
            + urlencode(
                {
                    "type": "best",
                    "storm": "09",
                    "basin": "al",
                    "year": "2022",
                }
            )
        )
        m.get(url, json=NHC_IAN_BESTRACK_JSON)
        s = MetGetTrack(args)
        s.get_track()
        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == NHC_IAN_BESTRACK_JSON["body"]["geojson"]


def test_forecast_track(capfd) -> None:
    """
    Tests the forecast track data
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    import json

    args = argparse.Namespace()
    args.type = "forecast"
    args.storm = 9
    args.year = 2022
    args.basin = "al"
    args.advisory = 12
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with requests_mock.Mocker() as m:
        url = (
            METGET_DMY_ENDPOINT
            + "/stormtrack?"
            + urlencode(
                {
                    "type": "forecast",
                    "storm": "09",
                    "basin": "al",
                    "advisory": "012",
                    "year": "2022",
                }
            )
        )
        m.get(url, json=NHC_IAN_FORECAST_JSON)
        s = MetGetTrack(args)
        s.get_track()
        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == NHC_IAN_FORECAST_JSON["body"]["geojson"]
