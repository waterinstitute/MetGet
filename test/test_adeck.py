import argparse
import json
import os
from datetime import datetime

import requests_mock

from metget.metget_adeck import metget_adeck

from .adeck_data import (
    ADECK_ALL_2024_14_20241009_PRETTYTABLE,
    ADECK_ALL_2024_14_20241009_RESPONSE,
    ADECK_AVNO_2024_14L_20241009_PRETTYTABLE,
    ADECK_AVNO_2024_14L_20241009_RESPONSE,
    ADECK_AVNO_2024_ALL_20241009_PRETTYTABLE,
    ADECK_AVNO_2024_ALL_20241009_RESPONSE,
)

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2


def test_adeck_json_single_storm(capfd) -> None:
    """
    **TEST PURPOSE**: Validates A-deck data retrieval for a single storm in JSON format
    **MODULE**: metget_adeck.metget_adeck
    **SCENARIO**: Request A-deck track data for Hurricane 14L in 2024 from AVNO model
    **INPUT**: Storm 14, year 2024, basin AL, model AVNO, cycle 2024-10-09T00:00, format JSON
    **EXPECTED**: Returns storm track data as JSON matching expected response structure
    **COVERAGE**: Tests successful single storm JSON response handling and output formatting
    """
    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="json",
        output=None,
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
    **TEST PURPOSE**: Validates A-deck data retrieval for a single storm in pretty-printed table format
    **MODULE**: metget_adeck.metget_adeck
    **SCENARIO**: Request A-deck track data for Hurricane 14L in 2024 from AVNO model
    **INPUT**: Storm 14, year 2024, basin AL, model AVNO, cycle 2024-10-09T00:00, format pretty
    **EXPECTED**: Returns storm track data as formatted table matching expected layout
    **COVERAGE**: Tests pretty-print formatting functionality and table output generation
    """
    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="pretty",
        output=None,
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
    **TEST PURPOSE**: Validates A-deck data retrieval for all storms in JSON format
    **MODULE**: metget_adeck.metget_adeck
    **SCENARIO**: Request A-deck track data for all storms in 2024 from AVNO model
    **INPUT**: Storm 'all', year 2024, basin AL, model AVNO, cycle 2024-10-09T00:00, format JSON
    **EXPECTED**: Returns multiple storm tracks data as JSON with 'storm_tracks' structure
    **COVERAGE**: Tests bulk storm data retrieval and multi-storm JSON response handling
    """
    args = argparse.Namespace(
        storm="all",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="json",
        output=None,
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
    **TEST PURPOSE**: Validates A-deck data retrieval for all storms in pretty-printed table format
    **MODULE**: metget_adeck.metget_adeck
    **SCENARIO**: Request A-deck track data for all storms in 2024 from AVNO model
    **INPUT**: Storm 'all', year 2024, basin AL, model AVNO, cycle 2024-10-09T00:00, format pretty
    **EXPECTED**: Returns multiple storm tracks as formatted table with consolidated layout
    **COVERAGE**: Tests bulk data pretty-print formatting and multi-storm table generation
    """
    args = argparse.Namespace(
        storm="all",
        year="2024",
        basin="AL",
        model="AVNO",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="pretty",
        output=None,
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
    **TEST PURPOSE**: Validates A-deck data retrieval for all models of a single storm with file output
    **MODULE**: metget_adeck.metget_adeck
    **SCENARIO**: Request A-deck track data for Hurricane 14L from all available models
    **INPUT**: Storm 14, year 2024, basin AL, model 'all', cycle 2024-10-09T00:00, JSON output to file
    **EXPECTED**: Creates JSON file containing storm tracks from multiple models
    **COVERAGE**: Tests multi-model data retrieval, file output functionality, and data aggregation
    """
    output_file_name = "pytest_track.json"

    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="all",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="json",
        output=output_file_name,
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/all/14/2024-10-09T00:00",
            json=ADECK_ALL_2024_14_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)

        # Read the output file
        with open(output_file_name) as f:
            output_file = f.read()
            output_file_dict = json.loads(output_file)

        # Remove the output file
        os.remove(output_file_name)

        # Check the output
        assert (
            output_file_dict
            == ADECK_ALL_2024_14_20241009_RESPONSE["body"]["storm_tracks"]
        )


def test_adeck_all_models_one_storm_pretty(capfd) -> None:
    """
    **TEST PURPOSE**: Validates A-deck data retrieval for all models of a single storm in table format
    **MODULE**: metget_adeck.metget_adeck
    **SCENARIO**: Request A-deck track data for Hurricane 14L from all available models
    **INPUT**: Storm 14, year 2024, basin AL, model 'all', cycle 2024-10-09T00:00, format pretty
    **EXPECTED**: Returns comparative table showing track data from multiple models
    **COVERAGE**: Tests multi-model data aggregation and comparative table formatting
    """
    args = argparse.Namespace(
        storm="14",
        year="2024",
        basin="AL",
        model="all",
        cycle=datetime(2024, 10, 9, 0, 0),
        format="pretty",
        output=None,
        endpoint=METGET_DMY_ENDPOINT,
        apikey=METGET_DMY_APIKEY,
        api_version=METGET_API_VERSION,
    )

    with requests_mock.Mocker() as m:
        m.get(
            f"{METGET_DMY_ENDPOINT}/adeck/2024/AL/all/14/2024-10-09T00:00",
            json=ADECK_ALL_2024_14_20241009_RESPONSE,
        )

        # Call the function and capture the screen output
        metget_adeck(args)
        screen_output = capfd.readouterr().out

        # Check the output
        assert screen_output == ADECK_ALL_2024_14_20241009_PRETTYTABLE
