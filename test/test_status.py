import requests_mock
import argparse
from metget_client.metget_status import MetGetStatus

METGET_DMY_ENDPOINT = "https://metget.dmy.pw"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2

GFS_STATUS_JSON = {
    "statusCode": 200,
    "body": {
        "meteorological_source": "gfs",
        "request_limit_days": 3,
        "request_limit_start": "2023-07-08 01:18:36",
        "request_limit_end": "2023-07-11 01:18:36",
        "min_forecast_date": "2023-07-08 06:00:00",
        "max_forecast_date": "2023-07-26 18:00:00",
        "first_available_cycle": "2023-07-08 06:00:00",
        "latest_available_cycle": "2023-07-10 18:00:00",
        "latest_available_cycle_length": 384,
        "latest_complete_cycle": "2023-07-10 18:00:00",
        "complete_cycle_length": 384,
        "cycles_complete": [
            "2023-07-10 18:00:00",
            "2023-07-10 12:00:00",
            "2023-07-10 06:00:00",
            "2023-07-10 00:00:00",
            "2023-07-09 18:00:00",
            "2023-07-09 12:00:00",
            "2023-07-09 06:00:00",
            "2023-07-09 00:00:00",
            "2023-07-08 18:00:00",
            "2023-07-08 12:00:00",
            "2023-07-08 06:00:00",
        ],
        "cycles": [
            {"cycle": "2023-07-10 18:00:00", "duration": 384},
            {"cycle": "2023-07-10 12:00:00", "duration": 384},
            {"cycle": "2023-07-10 06:00:00", "duration": 384},
            {"cycle": "2023-07-10 00:00:00", "duration": 384},
            {"cycle": "2023-07-09 18:00:00", "duration": 384},
            {"cycle": "2023-07-09 12:00:00", "duration": 384},
            {"cycle": "2023-07-09 06:00:00", "duration": 384},
            {"cycle": "2023-07-09 00:00:00", "duration": 384},
            {"cycle": "2023-07-08 18:00:00", "duration": 384},
            {"cycle": "2023-07-08 12:00:00", "duration": 384},
            {"cycle": "2023-07-08 06:00:00", "duration": 384},
        ],
    },
}

HWRF_STATUS_JSON = {
    "statusCode": 200,
    "body": {
        "invest93b": {
            "min_forecast_date": "2023-06-09 00:00:00",
            "max_forecast_date": "2023-06-14 06:00:00",
            "first_available_cycle": "2023-06-09 00:00:00",
            "latest_available_cycle": "2023-06-09 00:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-09 00:00:00",
            "complete_cycle_length": 126,
            "cycles": [{"cycle": "2023-06-09 00:00:00", "duration": 126}],
            "cycles_complete": ["2023-06-09 00:00:00"],
        },
        "invest92e": {
            "min_forecast_date": "2023-06-28 12:00:00",
            "max_forecast_date": "2023-07-04 00:00:00",
            "first_available_cycle": "2023-06-28 12:00:00",
            "latest_available_cycle": "2023-06-28 18:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-28 18:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-28 18:00:00", "duration": 126},
                {"cycle": "2023-06-28 12:00:00", "duration": 126},
            ],
            "cycles_complete": ["2023-06-28 18:00:00", "2023-06-28 12:00:00"],
        },
        "four04l": {
            "min_forecast_date": "2023-06-22 06:00:00",
            "max_forecast_date": "2023-06-28 06:00:00",
            "first_available_cycle": "2023-06-22 06:00:00",
            "latest_available_cycle": "2023-06-23 00:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-23 00:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-23 00:00:00", "duration": 126},
                {"cycle": "2023-06-22 18:00:00", "duration": 126},
                {"cycle": "2023-06-22 12:00:00", "duration": 126},
                {"cycle": "2023-06-22 06:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-23 00:00:00",
                "2023-06-22 18:00:00",
                "2023-06-22 12:00:00",
                "2023-06-22 06:00:00",
            ],
        },
        "invest92l": {
            "min_forecast_date": "2023-06-17 00:00:00",
            "max_forecast_date": "2023-06-24 18:00:00",
            "first_available_cycle": "2023-06-17 00:00:00",
            "latest_available_cycle": "2023-06-19 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-19 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-19 12:00:00", "duration": 126},
                {"cycle": "2023-06-19 06:00:00", "duration": 126},
                {"cycle": "2023-06-19 00:00:00", "duration": 126},
                {"cycle": "2023-06-18 12:00:00", "duration": 126},
                {"cycle": "2023-06-18 06:00:00", "duration": 126},
                {"cycle": "2023-06-18 00:00:00", "duration": 126},
                {"cycle": "2023-06-17 18:00:00", "duration": 126},
                {"cycle": "2023-06-17 12:00:00", "duration": 126},
                {"cycle": "2023-06-17 06:00:00", "duration": 126},
                {"cycle": "2023-06-17 00:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-19 12:00:00",
                "2023-06-19 06:00:00",
                "2023-06-19 00:00:00",
                "2023-06-18 12:00:00",
                "2023-06-18 06:00:00",
                "2023-06-18 00:00:00",
                "2023-06-17 18:00:00",
                "2023-06-17 12:00:00",
                "2023-06-17 06:00:00",
                "2023-06-17 00:00:00",
            ],
        },
        "two02a": {
            "min_forecast_date": "2023-06-06 12:00:00",
            "max_forecast_date": "2023-06-11 18:00:00",
            "first_available_cycle": "2023-06-06 12:00:00",
            "latest_available_cycle": "2023-06-06 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-06 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [{"cycle": "2023-06-06 12:00:00", "duration": 126}],
            "cycles_complete": ["2023-06-06 12:00:00"],
        },
        "three03w": {
            "min_forecast_date": "2023-06-06 00:00:00",
            "max_forecast_date": "2023-06-11 18:00:00",
            "first_available_cycle": "2023-06-06 00:00:00",
            "latest_available_cycle": "2023-06-06 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-06 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-06 12:00:00", "duration": 126},
                {"cycle": "2023-06-06 00:00:00", "duration": 126},
            ],
            "cycles_complete": ["2023-06-06 12:00:00", "2023-06-06 00:00:00"],
        },
        "arlene02l": {
            "min_forecast_date": "2023-06-02 18:00:00",
            "max_forecast_date": "2023-06-08 18:00:00",
            "first_available_cycle": "2023-06-02 18:00:00",
            "latest_available_cycle": "2023-06-03 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-03 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-03 12:00:00", "duration": 126},
                {"cycle": "2023-06-03 06:00:00", "duration": 126},
                {"cycle": "2023-06-03 00:00:00", "duration": 126},
                {"cycle": "2023-06-02 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-03 12:00:00",
                "2023-06-03 06:00:00",
                "2023-06-03 00:00:00",
                "2023-06-02 18:00:00",
            ],
        },
        "mawar02w": {
            "min_forecast_date": "2023-06-01 00:00:00",
            "max_forecast_date": "2023-06-08 12:00:00",
            "first_available_cycle": "2023-06-01 00:00:00",
            "latest_available_cycle": "2023-06-03 06:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-03 06:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-03 06:00:00", "duration": 126},
                {"cycle": "2023-06-03 00:00:00", "duration": 126},
                {"cycle": "2023-06-02 18:00:00", "duration": 126},
                {"cycle": "2023-06-02 12:00:00", "duration": 126},
                {"cycle": "2023-06-02 06:00:00", "duration": 126},
                {"cycle": "2023-06-02 00:00:00", "duration": 126},
                {"cycle": "2023-06-01 18:00:00", "duration": 126},
                {"cycle": "2023-06-01 12:00:00", "duration": 126},
                {"cycle": "2023-06-01 06:00:00", "duration": 126},
                {"cycle": "2023-06-01 00:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-03 06:00:00",
                "2023-06-03 00:00:00",
                "2023-06-02 18:00:00",
                "2023-06-02 12:00:00",
                "2023-06-02 06:00:00",
                "2023-06-02 00:00:00",
                "2023-06-01 18:00:00",
                "2023-06-01 12:00:00",
                "2023-06-01 06:00:00",
                "2023-06-01 00:00:00",
            ],
        },
        "biparjoy02a": {
            "min_forecast_date": "2023-06-06 18:00:00",
            "max_forecast_date": "2023-06-21 18:00:00",
            "first_available_cycle": "2023-06-06 18:00:00",
            "latest_available_cycle": "2023-06-16 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-16 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-16 12:00:00", "duration": 126},
                {"cycle": "2023-06-16 06:00:00", "duration": 126},
                {"cycle": "2023-06-16 00:00:00", "duration": 126},
                {"cycle": "2023-06-15 18:00:00", "duration": 126},
                {"cycle": "2023-06-15 12:00:00", "duration": 126},
                {"cycle": "2023-06-15 06:00:00", "duration": 126},
                {"cycle": "2023-06-15 00:00:00", "duration": 126},
                {"cycle": "2023-06-14 18:00:00", "duration": 126},
                {"cycle": "2023-06-14 12:00:00", "duration": 126},
                {"cycle": "2023-06-14 06:00:00", "duration": 126},
                {"cycle": "2023-06-14 00:00:00", "duration": 126},
                {"cycle": "2023-06-13 18:00:00", "duration": 126},
                {"cycle": "2023-06-13 12:00:00", "duration": 126},
                {"cycle": "2023-06-13 06:00:00", "duration": 126},
                {"cycle": "2023-06-13 00:00:00", "duration": 126},
                {"cycle": "2023-06-12 18:00:00", "duration": 126},
                {"cycle": "2023-06-12 06:00:00", "duration": 126},
                {"cycle": "2023-06-12 00:00:00", "duration": 126},
                {"cycle": "2023-06-11 18:00:00", "duration": 126},
                {"cycle": "2023-06-11 12:00:00", "duration": 126},
                {"cycle": "2023-06-11 06:00:00", "duration": 126},
                {"cycle": "2023-06-11 00:00:00", "duration": 126},
                {"cycle": "2023-06-10 18:00:00", "duration": 126},
                {"cycle": "2023-06-10 12:00:00", "duration": 126},
                {"cycle": "2023-06-10 06:00:00", "duration": 126},
                {"cycle": "2023-06-10 00:00:00", "duration": 126},
                {"cycle": "2023-06-09 18:00:00", "duration": 126},
                {"cycle": "2023-06-09 12:00:00", "duration": 126},
                {"cycle": "2023-06-09 06:00:00", "duration": 126},
                {"cycle": "2023-06-09 00:00:00", "duration": 126},
                {"cycle": "2023-06-08 18:00:00", "duration": 126},
                {"cycle": "2023-06-08 12:00:00", "duration": 126},
                {"cycle": "2023-06-08 06:00:00", "duration": 126},
                {"cycle": "2023-06-08 00:00:00", "duration": 126},
                {"cycle": "2023-06-07 18:00:00", "duration": 126},
                {"cycle": "2023-06-07 12:00:00", "duration": 126},
                {"cycle": "2023-06-07 06:00:00", "duration": 126},
                {"cycle": "2023-06-07 00:00:00", "duration": 126},
                {"cycle": "2023-06-06 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-16 12:00:00",
                "2023-06-16 06:00:00",
                "2023-06-16 00:00:00",
                "2023-06-15 18:00:00",
                "2023-06-15 12:00:00",
                "2023-06-15 06:00:00",
                "2023-06-15 00:00:00",
                "2023-06-14 18:00:00",
                "2023-06-14 12:00:00",
                "2023-06-14 06:00:00",
                "2023-06-14 00:00:00",
                "2023-06-13 18:00:00",
                "2023-06-13 12:00:00",
                "2023-06-13 06:00:00",
                "2023-06-13 00:00:00",
                "2023-06-12 18:00:00",
                "2023-06-12 06:00:00",
                "2023-06-12 00:00:00",
                "2023-06-11 18:00:00",
                "2023-06-11 12:00:00",
                "2023-06-11 06:00:00",
                "2023-06-11 00:00:00",
                "2023-06-10 18:00:00",
                "2023-06-10 12:00:00",
                "2023-06-10 06:00:00",
                "2023-06-10 00:00:00",
                "2023-06-09 18:00:00",
                "2023-06-09 12:00:00",
                "2023-06-09 06:00:00",
                "2023-06-09 00:00:00",
                "2023-06-08 18:00:00",
                "2023-06-08 12:00:00",
                "2023-06-08 06:00:00",
                "2023-06-08 00:00:00",
                "2023-06-07 18:00:00",
                "2023-06-07 12:00:00",
                "2023-06-07 06:00:00",
                "2023-06-07 00:00:00",
                "2023-06-06 18:00:00",
            ],
        },
        "two02e": {
            "min_forecast_date": "2023-06-29 00:00:00",
            "max_forecast_date": "2023-07-04 18:00:00",
            "first_available_cycle": "2023-06-29 00:00:00",
            "latest_available_cycle": "2023-06-29 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-29 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-29 12:00:00", "duration": 126},
                {"cycle": "2023-06-29 06:00:00", "duration": 126},
                {"cycle": "2023-06-29 00:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-29 12:00:00",
                "2023-06-29 06:00:00",
                "2023-06-29 00:00:00",
            ],
        },
        "beatriz02e": {
            "min_forecast_date": "2023-06-29 18:00:00",
            "max_forecast_date": "2023-07-06 18:00:00",
            "first_available_cycle": "2023-06-29 18:00:00",
            "latest_available_cycle": "2023-07-01 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-07-01 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-07-01 12:00:00", "duration": 126},
                {"cycle": "2023-07-01 06:00:00", "duration": 126},
                {"cycle": "2023-07-01 00:00:00", "duration": 126},
                {"cycle": "2023-06-30 18:00:00", "duration": 126},
                {"cycle": "2023-06-30 12:00:00", "duration": 126},
                {"cycle": "2023-06-30 06:00:00", "duration": 126},
                {"cycle": "2023-06-30 00:00:00", "duration": 126},
                {"cycle": "2023-06-29 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-07-01 12:00:00",
                "2023-07-01 06:00:00",
                "2023-07-01 00:00:00",
                "2023-06-30 18:00:00",
                "2023-06-30 12:00:00",
                "2023-06-30 06:00:00",
                "2023-06-30 00:00:00",
                "2023-06-29 18:00:00",
            ],
        },
        "invest92a": {
            "min_forecast_date": "2023-06-05 06:00:00",
            "max_forecast_date": "2023-06-11 06:00:00",
            "first_available_cycle": "2023-06-05 06:00:00",
            "latest_available_cycle": "2023-06-06 00:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-06 00:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-06 00:00:00", "duration": 126},
                {"cycle": "2023-06-05 18:00:00", "duration": 126},
                {"cycle": "2023-06-05 12:00:00", "duration": 126},
                {"cycle": "2023-06-05 06:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-06 00:00:00",
                "2023-06-05 18:00:00",
                "2023-06-05 12:00:00",
                "2023-06-05 06:00:00",
            ],
        },
        "cindy04l": {
            "min_forecast_date": "2023-06-23 06:00:00",
            "max_forecast_date": "2023-07-01 06:00:00",
            "first_available_cycle": "2023-06-23 06:00:00",
            "latest_available_cycle": "2023-06-26 00:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-26 00:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-26 00:00:00", "duration": 126},
                {"cycle": "2023-06-25 18:00:00", "duration": 126},
                {"cycle": "2023-06-25 12:00:00", "duration": 126},
                {"cycle": "2023-06-25 06:00:00", "duration": 126},
                {"cycle": "2023-06-25 00:00:00", "duration": 126},
                {"cycle": "2023-06-24 18:00:00", "duration": 126},
                {"cycle": "2023-06-24 12:00:00", "duration": 126},
                {"cycle": "2023-06-24 06:00:00", "duration": 126},
                {"cycle": "2023-06-24 00:00:00", "duration": 126},
                {"cycle": "2023-06-23 18:00:00", "duration": 126},
                {"cycle": "2023-06-23 12:00:00", "duration": 126},
                {"cycle": "2023-06-23 06:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-26 00:00:00",
                "2023-06-25 18:00:00",
                "2023-06-25 12:00:00",
                "2023-06-25 06:00:00",
                "2023-06-25 00:00:00",
                "2023-06-24 18:00:00",
                "2023-06-24 12:00:00",
                "2023-06-24 06:00:00",
                "2023-06-24 00:00:00",
                "2023-06-23 18:00:00",
                "2023-06-23 12:00:00",
                "2023-06-23 06:00:00",
            ],
        },
        "invest91l": {
            "min_forecast_date": "2023-06-01 00:00:00",
            "max_forecast_date": "2023-06-06 18:00:00",
            "first_available_cycle": "2023-06-01 00:00:00",
            "latest_available_cycle": "2023-06-01 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-01 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-01 12:00:00", "duration": 126},
                {"cycle": "2023-06-01 06:00:00", "duration": 126},
                {"cycle": "2023-06-01 00:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-01 12:00:00",
                "2023-06-01 06:00:00",
                "2023-06-01 00:00:00",
            ],
        },
        "two02l": {
            "min_forecast_date": "2023-06-01 18:00:00",
            "max_forecast_date": "2023-06-07 18:00:00",
            "first_available_cycle": "2023-06-01 18:00:00",
            "latest_available_cycle": "2023-06-02 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-02 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-02 12:00:00", "duration": 126},
                {"cycle": "2023-06-02 06:00:00", "duration": 126},
                {"cycle": "2023-06-02 00:00:00", "duration": 126},
                {"cycle": "2023-06-01 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-02 12:00:00",
                "2023-06-02 06:00:00",
                "2023-06-02 00:00:00",
                "2023-06-01 18:00:00",
            ],
        },
        "bret03l": {
            "min_forecast_date": "2023-06-19 18:00:00",
            "max_forecast_date": "2023-06-29 18:00:00",
            "first_available_cycle": "2023-06-19 18:00:00",
            "latest_available_cycle": "2023-06-24 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-24 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-24 12:00:00", "duration": 126},
                {"cycle": "2023-06-24 06:00:00", "duration": 126},
                {"cycle": "2023-06-24 00:00:00", "duration": 126},
                {"cycle": "2023-06-23 18:00:00", "duration": 126},
                {"cycle": "2023-06-23 12:00:00", "duration": 126},
                {"cycle": "2023-06-23 06:00:00", "duration": 126},
                {"cycle": "2023-06-23 00:00:00", "duration": 126},
                {"cycle": "2023-06-22 18:00:00", "duration": 126},
                {"cycle": "2023-06-22 12:00:00", "duration": 126},
                {"cycle": "2023-06-22 06:00:00", "duration": 126},
                {"cycle": "2023-06-22 00:00:00", "duration": 126},
                {"cycle": "2023-06-21 18:00:00", "duration": 126},
                {"cycle": "2023-06-21 12:00:00", "duration": 126},
                {"cycle": "2023-06-21 06:00:00", "duration": 126},
                {"cycle": "2023-06-21 00:00:00", "duration": 126},
                {"cycle": "2023-06-20 18:00:00", "duration": 126},
                {"cycle": "2023-06-20 12:00:00", "duration": 126},
                {"cycle": "2023-06-20 06:00:00", "duration": 126},
                {"cycle": "2023-06-20 00:00:00", "duration": 126},
                {"cycle": "2023-06-19 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-24 12:00:00",
                "2023-06-24 06:00:00",
                "2023-06-24 00:00:00",
                "2023-06-23 18:00:00",
                "2023-06-23 12:00:00",
                "2023-06-23 06:00:00",
                "2023-06-23 00:00:00",
                "2023-06-22 18:00:00",
                "2023-06-22 12:00:00",
                "2023-06-22 06:00:00",
                "2023-06-22 00:00:00",
                "2023-06-21 18:00:00",
                "2023-06-21 12:00:00",
                "2023-06-21 06:00:00",
                "2023-06-21 00:00:00",
                "2023-06-20 18:00:00",
                "2023-06-20 12:00:00",
                "2023-06-20 06:00:00",
                "2023-06-20 00:00:00",
                "2023-06-19 18:00:00",
            ],
        },
        "invest98w": {
            "min_forecast_date": "2023-06-02 12:00:00",
            "max_forecast_date": "2023-06-11 00:00:00",
            "first_available_cycle": "2023-06-02 12:00:00",
            "latest_available_cycle": "2023-06-05 18:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-05 18:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-05 18:00:00", "duration": 126},
                {"cycle": "2023-06-05 12:00:00", "duration": 126},
                {"cycle": "2023-06-05 06:00:00", "duration": 126},
                {"cycle": "2023-06-04 18:00:00", "duration": 126},
                {"cycle": "2023-06-04 12:00:00", "duration": 126},
                {"cycle": "2023-06-03 00:00:00", "duration": 126},
                {"cycle": "2023-06-02 18:00:00", "duration": 126},
                {"cycle": "2023-06-02 12:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-05 18:00:00",
                "2023-06-05 12:00:00",
                "2023-06-05 06:00:00",
                "2023-06-04 18:00:00",
                "2023-06-04 12:00:00",
                "2023-06-03 00:00:00",
                "2023-06-02 18:00:00",
                "2023-06-02 12:00:00",
            ],
        },
        "invest94e": {
            "min_forecast_date": "2023-07-10 06:00:00",
            "max_forecast_date": "2023-07-16 00:00:00",
            "first_available_cycle": "2023-07-10 06:00:00",
            "latest_available_cycle": "2023-07-10 18:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-07-10 18:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-07-10 18:00:00", "duration": 126},
                {"cycle": "2023-07-10 12:00:00", "duration": 126},
                {"cycle": "2023-07-10 06:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-07-10 18:00:00",
                "2023-07-10 12:00:00",
                "2023-07-10 06:00:00",
            ],
        },
        "invest93e": {
            "min_forecast_date": "2023-07-07 00:00:00",
            "max_forecast_date": "2023-07-14 12:00:00",
            "first_available_cycle": "2023-07-07 00:00:00",
            "latest_available_cycle": "2023-07-09 06:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-07-09 06:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-07-09 06:00:00", "duration": 126},
                {"cycle": "2023-07-09 00:00:00", "duration": 126},
                {"cycle": "2023-07-08 18:00:00", "duration": 126},
                {"cycle": "2023-07-08 12:00:00", "duration": 126},
                {"cycle": "2023-07-08 06:00:00", "duration": 126},
                {"cycle": "2023-07-08 00:00:00", "duration": 126},
                {"cycle": "2023-07-07 18:00:00", "duration": 126},
                {"cycle": "2023-07-07 12:00:00", "duration": 126},
                {"cycle": "2023-07-07 00:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-07-09 06:00:00",
                "2023-07-09 00:00:00",
                "2023-07-08 18:00:00",
                "2023-07-08 12:00:00",
                "2023-07-08 06:00:00",
                "2023-07-08 00:00:00",
                "2023-07-07 18:00:00",
                "2023-07-07 12:00:00",
                "2023-07-07 00:00:00",
            ],
        },
        "invest91e": {
            "min_forecast_date": "2023-06-26 18:00:00",
            "max_forecast_date": "2023-07-02 18:00:00",
            "first_available_cycle": "2023-06-26 18:00:00",
            "latest_available_cycle": "2023-06-27 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-27 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-27 12:00:00", "duration": 126},
                {"cycle": "2023-06-27 06:00:00", "duration": 126},
                {"cycle": "2023-06-27 00:00:00", "duration": 126},
                {"cycle": "2023-06-26 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-27 12:00:00",
                "2023-06-27 06:00:00",
                "2023-06-27 00:00:00",
                "2023-06-26 18:00:00",
            ],
        },
        "three03b": {
            "min_forecast_date": "2023-06-09 12:00:00",
            "max_forecast_date": "2023-06-15 06:00:00",
            "first_available_cycle": "2023-06-09 12:00:00",
            "latest_available_cycle": "2023-06-10 00:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-10 00:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-10 00:00:00", "duration": 126},
                {"cycle": "2023-06-09 18:00:00", "duration": 126},
                {"cycle": "2023-06-09 12:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-10 00:00:00",
                "2023-06-09 18:00:00",
                "2023-06-09 12:00:00",
            ],
        },
        "guchol03w": {
            "min_forecast_date": "2023-06-06 18:00:00",
            "max_forecast_date": "2023-06-18 18:00:00",
            "first_available_cycle": "2023-06-06 18:00:00",
            "latest_available_cycle": "2023-06-13 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-13 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-13 12:00:00", "duration": 126},
                {"cycle": "2023-06-13 06:00:00", "duration": 126},
                {"cycle": "2023-06-12 06:00:00", "duration": 126},
                {"cycle": "2023-06-12 00:00:00", "duration": 126},
                {"cycle": "2023-06-11 18:00:00", "duration": 126},
                {"cycle": "2023-06-11 12:00:00", "duration": 126},
                {"cycle": "2023-06-11 06:00:00", "duration": 126},
                {"cycle": "2023-06-11 00:00:00", "duration": 126},
                {"cycle": "2023-06-10 18:00:00", "duration": 126},
                {"cycle": "2023-06-10 12:00:00", "duration": 126},
                {"cycle": "2023-06-10 06:00:00", "duration": 126},
                {"cycle": "2023-06-10 00:00:00", "duration": 126},
                {"cycle": "2023-06-09 18:00:00", "duration": 126},
                {"cycle": "2023-06-09 12:00:00", "duration": 126},
                {"cycle": "2023-06-09 06:00:00", "duration": 126},
                {"cycle": "2023-06-09 00:00:00", "duration": 126},
                {"cycle": "2023-06-08 18:00:00", "duration": 126},
                {"cycle": "2023-06-08 12:00:00", "duration": 126},
                {"cycle": "2023-06-08 06:00:00", "duration": 126},
                {"cycle": "2023-06-08 00:00:00", "duration": 126},
                {"cycle": "2023-06-07 18:00:00", "duration": 126},
                {"cycle": "2023-06-07 12:00:00", "duration": 126},
                {"cycle": "2023-06-07 06:00:00", "duration": 126},
                {"cycle": "2023-06-07 00:00:00", "duration": 126},
                {"cycle": "2023-06-06 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-13 12:00:00",
                "2023-06-13 06:00:00",
                "2023-06-12 06:00:00",
                "2023-06-12 00:00:00",
                "2023-06-11 18:00:00",
                "2023-06-11 12:00:00",
                "2023-06-11 06:00:00",
                "2023-06-11 00:00:00",
                "2023-06-10 18:00:00",
                "2023-06-10 12:00:00",
                "2023-06-10 06:00:00",
                "2023-06-10 00:00:00",
                "2023-06-09 18:00:00",
                "2023-06-09 12:00:00",
                "2023-06-09 06:00:00",
                "2023-06-09 00:00:00",
                "2023-06-08 18:00:00",
                "2023-06-08 12:00:00",
                "2023-06-08 06:00:00",
                "2023-06-08 00:00:00",
                "2023-06-07 18:00:00",
                "2023-06-07 12:00:00",
                "2023-06-07 06:00:00",
                "2023-06-07 00:00:00",
                "2023-06-06 18:00:00",
            ],
        },
        "adrian01e": {
            "min_forecast_date": "2023-06-27 18:00:00",
            "max_forecast_date": "2023-07-07 18:00:00",
            "first_available_cycle": "2023-06-27 18:00:00",
            "latest_available_cycle": "2023-07-02 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-07-02 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-07-02 12:00:00", "duration": 126},
                {"cycle": "2023-07-02 06:00:00", "duration": 126},
                {"cycle": "2023-07-02 00:00:00", "duration": 126},
                {"cycle": "2023-07-01 18:00:00", "duration": 126},
                {"cycle": "2023-07-01 12:00:00", "duration": 126},
                {"cycle": "2023-07-01 06:00:00", "duration": 126},
                {"cycle": "2023-07-01 00:00:00", "duration": 126},
                {"cycle": "2023-06-30 18:00:00", "duration": 126},
                {"cycle": "2023-06-30 12:00:00", "duration": 126},
                {"cycle": "2023-06-30 06:00:00", "duration": 126},
                {"cycle": "2023-06-30 00:00:00", "duration": 126},
                {"cycle": "2023-06-29 18:00:00", "duration": 126},
                {"cycle": "2023-06-29 12:00:00", "duration": 126},
                {"cycle": "2023-06-29 06:00:00", "duration": 126},
                {"cycle": "2023-06-29 00:00:00", "duration": 126},
                {"cycle": "2023-06-28 18:00:00", "duration": 126},
                {"cycle": "2023-06-28 12:00:00", "duration": 126},
                {"cycle": "2023-06-28 06:00:00", "duration": 126},
                {"cycle": "2023-06-28 00:00:00", "duration": 126},
                {"cycle": "2023-06-27 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-07-02 12:00:00",
                "2023-07-02 06:00:00",
                "2023-07-02 00:00:00",
                "2023-07-01 18:00:00",
                "2023-07-01 12:00:00",
                "2023-07-01 06:00:00",
                "2023-07-01 00:00:00",
                "2023-06-30 18:00:00",
                "2023-06-30 12:00:00",
                "2023-06-30 06:00:00",
                "2023-06-30 00:00:00",
                "2023-06-29 18:00:00",
                "2023-06-29 12:00:00",
                "2023-06-29 06:00:00",
                "2023-06-29 00:00:00",
                "2023-06-28 18:00:00",
                "2023-06-28 12:00:00",
                "2023-06-28 06:00:00",
                "2023-06-28 00:00:00",
                "2023-06-27 18:00:00",
            ],
        },
        "invest93l": {
            "min_forecast_date": "2023-06-20 00:00:00",
            "max_forecast_date": "2023-06-27 06:00:00",
            "first_available_cycle": "2023-06-20 00:00:00",
            "latest_available_cycle": "2023-06-22 00:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-22 00:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-22 00:00:00", "duration": 126},
                {"cycle": "2023-06-21 18:00:00", "duration": 126},
                {"cycle": "2023-06-21 12:00:00", "duration": 126},
                {"cycle": "2023-06-21 06:00:00", "duration": 126},
                {"cycle": "2023-06-21 00:00:00", "duration": 126},
                {"cycle": "2023-06-20 18:00:00", "duration": 126},
                {"cycle": "2023-06-20 12:00:00", "duration": 126},
                {"cycle": "2023-06-20 06:00:00", "duration": 126},
                {"cycle": "2023-06-20 00:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-22 00:00:00",
                "2023-06-21 18:00:00",
                "2023-06-21 12:00:00",
                "2023-06-21 06:00:00",
                "2023-06-21 00:00:00",
                "2023-06-20 18:00:00",
                "2023-06-20 12:00:00",
                "2023-06-20 06:00:00",
                "2023-06-20 00:00:00",
            ],
        },
        "invest90e": {
            "min_forecast_date": "2023-06-17 18:00:00",
            "max_forecast_date": "2023-06-23 18:00:00",
            "first_available_cycle": "2023-06-17 18:00:00",
            "latest_available_cycle": "2023-06-18 12:00:00",
            "latest_available_cycle_length": 126,
            "latest_complete_cycle": "2023-06-18 12:00:00",
            "complete_cycle_length": 126,
            "cycles": [
                {"cycle": "2023-06-18 12:00:00", "duration": 126},
                {"cycle": "2023-06-18 06:00:00", "duration": 126},
                {"cycle": "2023-06-18 00:00:00", "duration": 126},
                {"cycle": "2023-06-17 18:00:00", "duration": 126},
            ],
            "cycles_complete": [
                "2023-06-18 12:00:00",
                "2023-06-18 06:00:00",
                "2023-06-18 00:00:00",
                "2023-06-17 18:00:00",
            ],
        },
    },
}


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
    assert (
        out == "Status for model: GFS (class: synoptic)\n"
        "+---------------------+---------------------+----------+\n"
        "|    Forecast Cycle   |       End Time      |  Status  |\n"
        "+---------------------+---------------------+----------+\n"
        "| 2023-07-10 18:00:00 | 2023-07-26 18:00:00 | complete |\n"
        "| 2023-07-10 12:00:00 | 2023-07-26 12:00:00 | complete |\n"
        "| 2023-07-10 06:00:00 | 2023-07-26 06:00:00 | complete |\n"
        "| 2023-07-10 00:00:00 | 2023-07-26 00:00:00 | complete |\n"
        "| 2023-07-09 18:00:00 | 2023-07-25 18:00:00 | complete |\n"
        "| 2023-07-09 12:00:00 | 2023-07-25 12:00:00 | complete |\n"
        "| 2023-07-09 06:00:00 | 2023-07-25 06:00:00 | complete |\n"
        "| 2023-07-09 00:00:00 | 2023-07-25 00:00:00 | complete |\n"
        "| 2023-07-08 18:00:00 | 2023-07-24 18:00:00 | complete |\n"
        "| 2023-07-08 12:00:00 | 2023-07-24 12:00:00 | complete |\n"
        "| 2023-07-08 06:00:00 | 2023-07-24 06:00:00 | complete |\n"
        "+---------------------+---------------------+----------+\n"
    )

    args.format = "json"

    s = MetGetStatus(args)
    with requests_mock.Mocker() as m:
        m.get(METGET_DMY_ENDPOINT + "/status?model=gfs", json=GFS_STATUS_JSON)
        s.get_status()
        out, err = capfd.readouterr()
        out = out.replace("'", '"')
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
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + "/status?model=hwrf&start=2023-06-01&end=2023-07-11",
            json=HWRF_STATUS_JSON,
        )
        s.get_status()
    out, err = capfd.readouterr()
    assert (
        out == "Status for HWRF Model Storms (class: synoptic-storm)\n"
        "+-------------+----------------------+---------------------+------------------------+----------------------+-------------+\n"
        "|       Storm | First Forecast Cycle | Last Forecast Cycle | Earliest Forecast Time | Latest Forecast Time | Cycle Count |\n"
        "+-------------+----------------------+---------------------+------------------------+----------------------+-------------+\n"
        "|   invest94e | 2023-07-10 06:00:00  | 2023-07-10 18:00:00 |  2023-07-10 06:00:00   | 2023-07-16 00:00:00  |           3 |\n"
        "|   invest93e | 2023-07-07 00:00:00  | 2023-07-09 06:00:00 |  2023-07-07 00:00:00   | 2023-07-14 12:00:00  |           9 |\n"
        "|  beatriz02e | 2023-06-29 18:00:00  | 2023-07-01 12:00:00 |  2023-06-29 18:00:00   | 2023-07-06 18:00:00  |           8 |\n"
        "|      two02e | 2023-06-29 00:00:00  | 2023-06-29 12:00:00 |  2023-06-29 00:00:00   | 2023-07-04 18:00:00  |           3 |\n"
        "|   invest92e | 2023-06-28 12:00:00  | 2023-06-28 18:00:00 |  2023-06-28 12:00:00   | 2023-07-04 00:00:00  |           2 |\n"
        "|   adrian01e | 2023-06-27 18:00:00  | 2023-07-02 12:00:00 |  2023-06-27 18:00:00   | 2023-07-07 18:00:00  |          20 |\n"
        "|   invest91e | 2023-06-26 18:00:00  | 2023-06-27 12:00:00 |  2023-06-26 18:00:00   | 2023-07-02 18:00:00  |           4 |\n"
        "|    cindy04l | 2023-06-23 06:00:00  | 2023-06-26 00:00:00 |  2023-06-23 06:00:00   | 2023-07-01 06:00:00  |          12 |\n"
        "|     four04l | 2023-06-22 06:00:00  | 2023-06-23 00:00:00 |  2023-06-22 06:00:00   | 2023-06-28 06:00:00  |           4 |\n"
        "|   invest93l | 2023-06-20 00:00:00  | 2023-06-22 00:00:00 |  2023-06-20 00:00:00   | 2023-06-27 06:00:00  |           9 |\n"
        "|     bret03l | 2023-06-19 18:00:00  | 2023-06-24 12:00:00 |  2023-06-19 18:00:00   | 2023-06-29 18:00:00  |          20 |\n"
        "|   invest90e | 2023-06-17 18:00:00  | 2023-06-18 12:00:00 |  2023-06-17 18:00:00   | 2023-06-23 18:00:00  |           4 |\n"
        "|   invest92l | 2023-06-17 00:00:00  | 2023-06-19 12:00:00 |  2023-06-17 00:00:00   | 2023-06-24 18:00:00  |          10 |\n"
        "|    three03b | 2023-06-09 12:00:00  | 2023-06-10 00:00:00 |  2023-06-09 12:00:00   | 2023-06-15 06:00:00  |           3 |\n"
        "|   invest93b | 2023-06-09 00:00:00  | 2023-06-09 00:00:00 |  2023-06-09 00:00:00   | 2023-06-14 06:00:00  |           1 |\n"
        "|   guchol03w | 2023-06-06 18:00:00  | 2023-06-13 12:00:00 |  2023-06-06 18:00:00   | 2023-06-18 18:00:00  |          25 |\n"
        "| biparjoy02a | 2023-06-06 18:00:00  | 2023-06-16 12:00:00 |  2023-06-06 18:00:00   | 2023-06-21 18:00:00  |          39 |\n"
        "|      two02a | 2023-06-06 12:00:00  | 2023-06-06 12:00:00 |  2023-06-06 12:00:00   | 2023-06-11 18:00:00  |           1 |\n"
        "|    three03w | 2023-06-06 00:00:00  | 2023-06-06 12:00:00 |  2023-06-06 00:00:00   | 2023-06-11 18:00:00  |           2 |\n"
        "|   invest92a | 2023-06-05 06:00:00  | 2023-06-06 00:00:00 |  2023-06-05 06:00:00   | 2023-06-11 06:00:00  |           4 |\n"
        "|   arlene02l | 2023-06-02 18:00:00  | 2023-06-03 12:00:00 |  2023-06-02 18:00:00   | 2023-06-08 18:00:00  |           4 |\n"
        "|   invest98w | 2023-06-02 12:00:00  | 2023-06-05 18:00:00 |  2023-06-02 12:00:00   | 2023-06-11 00:00:00  |           8 |\n"
        "|      two02l | 2023-06-01 18:00:00  | 2023-06-02 12:00:00 |  2023-06-01 18:00:00   | 2023-06-07 18:00:00  |           4 |\n"
        "|    mawar02w | 2023-06-01 00:00:00  | 2023-06-03 06:00:00 |  2023-06-01 00:00:00   | 2023-06-08 12:00:00  |          10 |\n"
        "|   invest91l | 2023-06-01 00:00:00  | 2023-06-01 12:00:00 |  2023-06-01 00:00:00   | 2023-06-06 18:00:00  |           3 |\n"
        "+-------------+----------------------+---------------------+------------------------+----------------------+-------------+\n"
    )

    args.format = "json"

    s = MetGetStatus(args)
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + "/status?model=hwrf&start=2023-06-01&end=2023-07-11",
            json=HWRF_STATUS_JSON,
        )
        s.get_status()
        out, err = capfd.readouterr()
        out = out.replace("'", '"')
        out_dict = json.loads(out)
        assert out_dict == HWRF_STATUS_JSON["body"]
