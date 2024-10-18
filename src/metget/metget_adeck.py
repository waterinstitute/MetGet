###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################
import argparse
import contextlib

from prettytable import PrettyTable


def metget_adeck(args: argparse.Namespace) -> None:
    """
    Get the A-Deck data from MetGet for the given parameters

    Args:
        args (argparse.Namespace): The arguments from the command line

    Raises:
        ValueError: If the parameters are invalid
    """
    import json

    import requests

    from .metget_environment import get_metget_environment_variables

    env = get_metget_environment_variables(args)
    headers = {"x-api-key": env["apikey"]}

    storm = args.storm
    year = args.year
    basin = args.basin.upper()
    model = args.model.upper()
    cycle = args.cycle.strftime("%Y-%m-%dT%H:%M")

    if basin not in ["AL", "EP", "CP"]:
        msg = "Invalid basin. Must be one of AL, EP, CP"
        raise ValueError(msg)

    with contextlib.suppress(ValueError):
        storm = int(storm)

    if isinstance(storm, str) and storm == "all":
        url = env["endpoint"] + f"/adeck/{year}/{basin}/{model}/{storm}/{cycle}"
    elif isinstance(storm, int):
        url = env["endpoint"] + f"/adeck/{year}/{basin}/{model}/{storm:02d}/{cycle}"
    else:
        msg = "Invalid storm. Must be an integer or 'all'"
        raise ValueError(msg)

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        msg = "Invalid request. Check the parameters and try again."
        raise ValueError(msg)
    response_data = response.json()

    track_data = response_data["body"]

    if args.format == "json":
        if storm == "all" or model.lower() == "all":
            print(json.dumps(track_data["storm_tracks"]))
        else:
            print(json.dumps(track_data["storm_track"]))
    elif args.format == "pretty":
        if storm == "all":
            table = print_table_all_storms(track_data)
        elif model.lower() == "all":
            table = print_table_all_models(track_data)
        else:
            table = print_table_single_storm_single_model(track_data)
        print(table)


def print_table_all_models(track_data: dict) -> PrettyTable:
    """
    Get a pretty table of all models for a given storm

    Args:
        track_data (dict): The track data from the MetGet API

    Returns:
        PrettyTable: A pretty table of the track data
    """
    table = PrettyTable(
        [
            "Model",
            "Min Fcst Pressure (mb)",
            "Max Fcst Wind Speed (mph)",
        ],
        sortby="Model",
    )

    for model in track_data["storm_tracks"]:
        minimum_pressure = 9999
        maximum_wind_speed = 0

        for snap in track_data["storm_tracks"][model]["features"]:
            if snap["properties"]["minimum_sea_level_pressure_mb"] != 0:
                minimum_pressure = min(
                    minimum_pressure,
                    snap["properties"]["minimum_sea_level_pressure_mb"],
                )

            if snap["properties"]["max_wind_speed_mph"] != 0:
                maximum_wind_speed = max(
                    maximum_wind_speed, snap["properties"]["max_wind_speed_mph"]
                )

        if minimum_pressure == 9999:
            minimum_pressure = "N/A"

        if maximum_wind_speed == 0:
            maximum_wind_speed = "N/A"

        table.add_row(
            [
                model,
                minimum_pressure,
                maximum_wind_speed,
            ]
        )

    return table


def print_table_all_storms(track_data: dict) -> PrettyTable:
    """
    Get a pretty table of all storms for a given model

    Args:
        track_data (dict): The track data from the MetGet API

    Returns:
        PrettyTable: A pretty table of the track data
    """
    table = PrettyTable(
        [
            "Storm",
            "Current Longitude",
            "Current Latitude",
            "Min Fcst Pressure (mb)",
            "Max Fcst Wind Speed (mph)",
        ],
        sortby="Storm",
    )

    for storm in track_data["storm_tracks"]:
        minimum_pressure = 9999
        maximum_wind_speed = 0
        current_longitude = track_data["storm_tracks"][storm]["features"][0][
            "geometry"
        ]["coordinates"][0]
        current_latitude = track_data["storm_tracks"][storm]["features"][0]["geometry"][
            "coordinates"
        ][1]

        for snap in track_data["storm_tracks"][storm]["features"]:
            pressure = snap["properties"]["minimum_sea_level_pressure_mb"]
            if pressure != 0:
                minimum_pressure = min(minimum_pressure, pressure)

            wind_speed = snap["properties"]["max_wind_speed_mph"]
            if wind_speed != 0:
                maximum_wind_speed = max(maximum_wind_speed, wind_speed)

        if minimum_pressure == 9999:
            minimum_pressure = "N/A"

        if maximum_wind_speed == 0:
            maximum_wind_speed = "N/A"

        table.add_row(
            [
                storm,
                current_longitude,
                current_latitude,
                minimum_pressure,
                maximum_wind_speed,
            ],
        )
    return table


def print_table_single_storm_single_model(track_data: dict) -> PrettyTable:
    """
    Get a pretty table of a single storm for a single model

    Args:
        track_data (dict): The track data from the MetGet API

    Returns:
        PrettyTable: A pretty table of the track data
    """
    table = PrettyTable(
        ["Time", "Longitude", "Latitude", "Pressure (mb)", "Wind Speed (mph)"]
    )

    for snap in track_data["storm_track"]["features"]:
        longitude = snap["geometry"]["coordinates"][0]
        latitude = snap["geometry"]["coordinates"][1]
        pressure = snap["properties"]["minimum_sea_level_pressure_mb"]
        wind_speed = snap["properties"]["max_wind_speed_mph"]
        snap_time = snap["properties"]["time_utc"]
        table.add_row([snap_time, longitude, latitude, pressure, wind_speed])

    return table
