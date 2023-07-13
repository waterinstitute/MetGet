import requests_mock
import argparse
from urllib.parse import urlencode
from metget_client.metget_status import MetGetStatus
from .status_json import *
from .status_text import *

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2


def test_get_status_gfs(capfd) -> None:
    """
    Tests the status command for the GFS model
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    import json

    args = argparse.Namespace()
    args.model = "gfs"
    args.format = "pretty"
    args.start = None
    args.end = None
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    s = MetGetStatus(args)
    with requests_mock.Mocker() as m:
        m.get(METGET_DMY_ENDPOINT + "/status?model=gfs", json=GFS_STATUS_JSON)
        s.get_status()
    out, err = capfd.readouterr()
    assert out == GFS_STATUS_TEXT

    args.format = "json"

    s = MetGetStatus(args)
    with requests_mock.Mocker() as m:
        m.get(METGET_DMY_ENDPOINT + "/status?model=gfs", json=GFS_STATUS_JSON)
        s.get_status()
        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == GFS_STATUS_JSON["body"]


def test_status_hwrf(capfd) -> None:
    """
    Tests the status command for the HWRF model

    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    import json
    from datetime import datetime

    args = argparse.Namespace()
    args.model = "hwrf"
    args.format = "pretty"
    args.start = datetime(2023, 6, 1)
    args.storm = None
    args.end = datetime(2023, 7, 11)
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    s = MetGetStatus(args)
    url = (
        METGET_DMY_ENDPOINT
        + "/status?"
        + urlencode({"model": "hwrf", "start": "2023-06-01", "end": "2023-07-11"})
    )
    with requests_mock.Mocker() as m:
        m.get(url, json=HWRF_STATUS_JSON)
        s.get_status()
    out, err = capfd.readouterr()
    assert out == HWRF_STATUS_TEXT

    args.format = "json"

    s = MetGetStatus(args)
    with requests_mock.Mocker() as m:
        m.get(url, json=HWRF_STATUS_JSON)
        s.get_status()
        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == HWRF_STATUS_JSON["body"]

    args.storm = "bret03l"
    s2 = MetGetStatus(args)
    url = (
        METGET_DMY_ENDPOINT
        + "/status?"
        + urlencode(
            {
                "model": "hwrf",
                "start": "2023-06-01",
                "end": "2023-07-11",
                "storm": "bret03l",
            }
        )
    )
    with requests_mock.Mocker() as m:
        m.get(url, json=HWRF_STATUS_BRET_JSON)
        s2.get_status()
        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == HWRF_STATUS_BRET_JSON["body"]

    args.format = "pretty"
    s3 = MetGetStatus(args)
    with requests_mock.Mocker() as m:
        m.get(url, json=HWRF_STATUS_BRET_JSON)
        s3.get_status()
        out, err = capfd.readouterr()
        assert out == HWRF_STATUS_BRET_TEXT


def test_status_nhc(capfd) -> None:
    """
    Tests the status command for the NHC data
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    from datetime import datetime
    import json

    args = argparse.Namespace()
    args.model = "nhc"
    args.start = datetime(2023, 6, 1)
    args.end = None
    args.storm = None
    args.basin = None
    args.format = "json"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with requests_mock.Mocker() as m:

        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode({"model": "nhc", "start": "2023-06-01"}),
            json=NHC_STATUS_JSON,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert json.loads(out) == NHC_STATUS_JSON["body"]

    args.format = "pretty"
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode({"model": "nhc", "start": "2023-06-01"}),
            json=NHC_STATUS_JSON,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert out == NHC_STATUS_TEXT


def test_status_gefs(capfd) -> None:
    """
    Tests the status command for the GEFS model
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    from datetime import datetime
    import json

    args = argparse.Namespace()
    args.model = "gefs"
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 8)
    args.ensemble_member = "c00"
    args.format = "json"
    args.storm = None
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode(
                {
                    "model": "gefs",
                    "start": "2023-06-01",
                    "end": "2023-06-08",
                    "member": "c00",
                }
            ),
            json=GEFS_STATUS_JSON_C00,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert json.loads(out) == GEFS_STATUS_JSON_C00["body"]["c00"]

    args.format = "pretty"
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode(
                {
                    "model": "gefs",
                    "start": "2023-06-01",
                    "end": "2023-06-08",
                    "member": "c00",
                }
            ),
            json=GEFS_STATUS_JSON_C00,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert out == GEFS_STATUS_TEXT_C00

    args.ensemble_member = None
    args.format = "json"
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode({"model": "gefs", "start": "2023-06-01", "end": "2023-06-08"}),
            json=GEFS_STATUS_JSON,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert json.loads(out) == GEFS_STATUS_JSON["body"]

    args.format = "pretty"
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode({"model": "gefs", "start": "2023-06-01", "end": "2023-06-08"}),
            json=GEFS_STATUS_JSON,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert out == GEFS_STATUS_TEXT


def test_status_ctcx(capfd) -> None:
    """
    Tests the status command for the COAMPS-CTCX model
    Args:
        capfd:

    Returns:
        None
    """
    from datetime import datetime
    import json

    args = argparse.Namespace()
    args.model = "ctcx"
    args.start = datetime(2022, 9, 26)
    args.end = datetime(2022, 9, 30)
    args.format = "json"
    args.storm = None
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode(
                {
                    "model": "ctcx",
                    "start": "2022-09-26",
                    "end": "2022-09-30",
                }
            ),
            json=COAMPS_CTCX_STATUS_JSON,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert json.loads(out) == COAMPS_CTCX_STATUS_JSON["body"]

    args.format = "pretty"
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT
            + "/status?"
            + urlencode(
                {
                    "model": "ctcx",
                    "start": "2022-09-26",
                    "end": "2022-09-30",
                }
            ),
            json=COAMPS_CTCX_STATUS_JSON,
        )
        s = MetGetStatus(args)
        s.get_status()
        out, err = capfd.readouterr()
        assert out == COAMPS_CTCX_STATUS_TEXT
