import argparse
import json
import os
from datetime import datetime
from urllib.parse import urlencode

import pytest
import requests_mock

from metget.metget_track import MetGetTrack, metget_track

from .track_json import NHC_IAN_BESTRACK_JSON, NHC_IAN_FORECAST_JSON

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2


def test_best_track(capfd) -> None:
    """
    **TEST PURPOSE**: Validates retrieval of historical best track data for completed storms
    **MODULE**: metget_track.MetGetTrack.get_track
    **SCENARIO**: Request best track data for Hurricane Ian (storm 09) in 2022 Atlantic season
    **INPUT**: Type 'besttrack', storm 9, year 2022, basin 'al', using environment variables
    **EXPECTED**: Returns GeoJSON format historical track data for the completed storm
    **COVERAGE**: Tests best track data retrieval, environment variable usage, and GeoJSON output
    """
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
    **TEST PURPOSE**: Validates retrieval of forecast track data for specific storm advisory
    **MODULE**: metget_track.MetGetTrack.get_track
    **SCENARIO**: Request forecast track for Hurricane Ian (storm 09) advisory 012 in 2022
    **INPUT**: Type 'forecast', storm 9, year 2022, basin 'al', advisory 12, direct API credentials
    **EXPECTED**: Returns GeoJSON format forecast track data for the specified advisory
    **COVERAGE**: Tests forecast track retrieval, advisory-specific data, and direct credential usage
    """
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


def test_track_missing_storm_validation() -> None:
    """
    **TEST PURPOSE**: Tests validation when storm is not specified (Lines 54-55)

    **SCENARIO**: When args.storm is None, should raise ValueError with appropriate message

    **WHY CRITICAL**: Storm is a required parameter for track requests

    **COVERAGE**: Covers previously untested lines 54-55 in get_track()
    """
    args = argparse.Namespace()
    args.type = "besttrack"
    args.storm = None  # Missing storm
    args.year = 2022
    args.basin = "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    track = MetGetTrack(args)
    with pytest.raises(ValueError, match="Storm must be specified for track data"):
        track.get_track()


def test_track_missing_type_validation() -> None:
    """
    **TEST PURPOSE**: Tests validation when type is not specified (Lines 58-59)

    **SCENARIO**: When args.type is None, should raise ValueError with appropriate message

    **WHY CRITICAL**: Type is a required parameter for track requests

    **COVERAGE**: Covers previously untested lines 58-59 in get_track()
    """
    args = argparse.Namespace()
    args.type = None  # Missing type
    args.storm = 9
    args.year = 2022
    args.basin = "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    track = MetGetTrack(args)
    with pytest.raises(ValueError, match="Type must be specified for track data"):
        track.get_track()


def test_track_default_basin_assignment(capfd) -> None:
    """
    **TEST PURPOSE**: Tests default basin assignment when not specified (Line 63)

    **SCENARIO**: When args.basin is None, should default to "al" (Atlantic)

    **WHY CRITICAL**: Basin defaults should work correctly for user convenience

    **COVERAGE**: Covers previously untested line 63 in get_track()
    """
    args = argparse.Namespace()
    args.type = "besttrack"
    args.storm = 9
    args.year = 2022
    args.basin = None  # Will be set to default "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with requests_mock.Mocker() as m:
        # Expect the default basin "al" to be used in the request
        url = (
            METGET_DMY_ENDPOINT
            + "/stormtrack?"
            + urlencode(
                {
                    "type": "best",
                    "storm": "09",
                    "basin": "al",  # Default basin
                    "year": "2022",
                }
            )
        )
        m.get(url, json=NHC_IAN_BESTRACK_JSON)

        track = MetGetTrack(args)
        track.get_track()

        # Verify the basin was set to default
        assert args.basin == "al"

        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == NHC_IAN_BESTRACK_JSON["body"]["geojson"]


def test_track_default_year_assignment(capfd) -> None:
    """
    **TEST PURPOSE**: Tests default year assignment when not specified (Line 67)

    **SCENARIO**: When args.year is None, should default to current year

    **WHY CRITICAL**: Year defaults should work correctly for user convenience

    **COVERAGE**: Covers previously untested line 67 in get_track()
    """
    args = argparse.Namespace()
    args.type = "besttrack"
    args.storm = 9
    args.year = None  # Will be set to current year
    args.basin = "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    current_year = datetime.now().year

    with requests_mock.Mocker() as m:
        # Expect the current year to be used in the request
        url = (
            METGET_DMY_ENDPOINT
            + "/stormtrack?"
            + urlencode(
                {
                    "type": "best",
                    "storm": "09",
                    "basin": "al",
                    "year": str(current_year),  # Current year
                }
            )
        )
        m.get(url, json=NHC_IAN_BESTRACK_JSON)

        track = MetGetTrack(args)
        track.get_track()

        # Verify the year was set to current year
        assert args.year == current_year

        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == NHC_IAN_BESTRACK_JSON["body"]["geojson"]


def test_track_forecast_missing_advisory_validation() -> None:
    """
    **TEST PURPOSE**: Tests validation when advisory is missing for forecast type (Lines 80-81)

    **SCENARIO**: When type is "forecast" but args.advisory is None, should raise ValueError

    **WHY CRITICAL**: Advisory is required for forecast track requests

    **COVERAGE**: Covers previously untested lines 80-81 in get_track()
    """
    args = argparse.Namespace()
    args.type = "forecast"
    args.storm = 9
    args.year = 2022
    args.basin = "al"
    args.advisory = None  # Missing advisory for forecast
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    track = MetGetTrack(args)
    with pytest.raises(
        ValueError, match="Advisory must be specified for forecast track data"
    ):
        track.get_track()


def test_track_invalid_type_validation() -> None:
    """
    **TEST PURPOSE**: Tests validation when invalid type is specified (Lines 92-93)

    **SCENARIO**: When type is neither "besttrack" nor "forecast", should raise ValueError

    **WHY CRITICAL**: Only specific track types are supported by the API

    **COVERAGE**: Covers previously untested lines 92-93 in get_track()
    """
    args = argparse.Namespace()
    args.type = "invalid_type"  # Invalid type
    args.storm = 9
    args.year = 2022
    args.basin = "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    track = MetGetTrack(args)
    with pytest.raises(ValueError, match="Type must be besttrack or forecast"):
        track.get_track()


def test_track_error_response_handling(capfd) -> None:
    """
    **TEST PURPOSE**: Tests error response handling when API returns non-200 status (Lines 102-103)

    **SCENARIO**: When API returns error status code, should print error information

    **WHY CRITICAL**: Proper error handling for API failures

    **COVERAGE**: Covers previously untested lines 102-103 in get_track()
    """
    args = argparse.Namespace()
    args.type = "besttrack"
    args.storm = 9
    args.year = 2022
    args.basin = "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    error_response = {
        "error": "Storm not found",
        "message": "The requested storm does not exist",
    }

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
        # Mock a 404 error response
        m.get(url, json=error_response, status_code=404)

        track = MetGetTrack(args)
        track.get_track()

        out, err = capfd.readouterr()
        assert "Error: 404" in out
        # Verify the error response is printed as JSON
        error_output = json.loads(out.split("\n")[1])  # Second line contains the JSON
        assert error_output == error_response


def test_metget_track_function(capfd) -> None:
    """
    **TEST PURPOSE**: Tests the metget_track wrapper function (Lines 116-117)

    **SCENARIO**: Tests that the function properly creates MetGetTrack instance and calls get_track

    **WHY CRITICAL**: This is the main entry point function for track functionality

    **COVERAGE**: Covers previously untested lines 116-117 in metget_track()
    """
    args = argparse.Namespace()
    args.type = "besttrack"
    args.storm = 9
    args.year = 2022
    args.basin = "al"
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

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

        # Test the wrapper function
        metget_track(args)

        out, err = capfd.readouterr()
        out_dict = json.loads(out)
        assert out_dict == NHC_IAN_BESTRACK_JSON["body"]["geojson"]
