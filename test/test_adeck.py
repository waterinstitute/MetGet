import argparse
import json
from datetime import datetime
from test.adeck_data import ADECK_AVNO_2024_14L_20241009_PRETTYTABLE

import requests_mock

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2


def test_adeck_json_single_storm(capfd) -> None:
    """
    Test that a single storm in the A-deck JSON format is returned correctly
    """
    from metget.metget_adeck import metget_adeck

    from .adeck_data import (
        ADECK_AVNO_2024_14L_20241009_RESPONSE,
    )

    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="json",
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/AVNO/14/2024-10-09T00:00",
            json=ADECK_AVNO_2024_14L_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out
        screen_output_dict = json.loads(screen_output)

        # Check the output
        assert (
            screen_output_dict
            == ADECK_AVNO_2024_14L_20241009_RESPONSE["body"]["storm_track"]
        )


def test_adeck_pretty_single_storm(capfd) -> None:
    """
    Test that a single storm in the A-deck pretty format is returned correctly
    """
    from metget.metget_adeck import metget_adeck

    from .adeck_data import ADECK_AVNO_2024_14L_20241009_RESPONSE

    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="pretty",
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/AVNO/14/2024-10-09T00:00",
            json=ADECK_AVNO_2024_14L_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out

        # Check the output
        assert screen_output == ADECK_AVNO_2024_14L_20241009_PRETTYTABLE


def test_adeck_json_all_storms(capfd) -> None:
    """
    Test that all storms in the A-deck JSON format are returned correctly
    """
    from metget.metget_adeck import metget_adeck

    from .adeck_data import (
        ADECK_AVNO_2024_ALL_20241009_RESPONSE,
    )

    args = argparse.Namespace(
        storm="all",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="json",
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/AVNO/all/2024-10-09T00:00",
            json=ADECK_AVNO_2024_ALL_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out
        screen_output_dict = json.loads(screen_output)

        # Check the output
        assert (
            screen_output_dict
            == ADECK_AVNO_2024_ALL_20241009_RESPONSE["body"]["storm_tracks"]
        )


def test_adeck_pretty_all_storms(capfd) -> None:
    """
    Test that all storms in the A-deck pretty format are returned correctly
    """
    from metget.metget_adeck import metget_adeck

    from .adeck_data import (
        ADECK_AVNO_2024_ALL_20241009_PRETTYTABLE,
        ADECK_AVNO_2024_ALL_20241009_RESPONSE,
    )

    args = argparse.Namespace(
        storm="all",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="pretty",
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/AVNO/all/2024-10-09T00:00",
            json=ADECK_AVNO_2024_ALL_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out

        # Check the output
        assert screen_output == ADECK_AVNO_2024_ALL_20241009_PRETTYTABLE


def test_adeck_all_models_one_storm(capfd) -> None:
    """
    Test that all models for one storm in the A-deck pretty format are returned correctly
    """
    from metget.metget_adeck import metget_adeck

    from .adeck_data import ADEC_ALL_2024_14_20241009_RESPONSE

    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="all",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="json",
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/all/14/2024-10-09T00:00",
            json=ADEC_ALL_2024_14_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out
        screen_output_dict = json.loads(screen_output)

        # Check the output
        assert (
            screen_output_dict
            == ADEC_ALL_2024_14_20241009_RESPONSE["body"]["storm_tracks"]
        )


def test_adeck_all_models_one_storm_pretty(capfd) -> None:
    """
    Test that all models for one storm in the A-deck pretty format are returned correctly
    """
    from metget.metget_adeck import metget_adeck

    from .adeck_data import (
        ADEC_ALL_2024_14_20241009_PRETTYTABLE,
        ADEC_ALL_2024_14_20241009_RESPONSE,
    )

    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="all",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="pretty",
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/all/14/2024-10-09T00:00",
            json=ADEC_ALL_2024_14_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out

        # Check the output
        assert screen_output == ADEC_ALL_2024_14_20241009_PRETTYTABLE
