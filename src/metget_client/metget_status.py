#!/usr/bin/env python3
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


class MetGetStatus:
    def __init__(self, args: argparse.Namespace):
        """
        This method is used to initialize the MetGet status command

        Args:
            args: The arguments passed to the command line

        Returns:
            None
        """
        from .metget_environment import get_metget_environment_variables

        self.__args = args
        self.__environment = get_metget_environment_variables(args)
        self.__model_class = None

        if self.__environment["api_version"] == 1:
            raise RuntimeError(
                "API version 1 is not supported with the status command. You should query the endpoint directly."
            )

    def get_status(self) -> None:
        """
        This method is used to get the status of the metget data
        """
        from .metget_data import MODEL_TYPES

        model = self.__args.model
        self.__model_class = MODEL_TYPES[model]

        if self.__model_class == "synoptic":
            self.__status_synoptic(model)
        elif self.__model_class == "synoptic-storm":
            self.__status_synoptic_storm(model)
        elif self.__model_class == "ensemble":
            self.__status_ensemble(model)
        elif self.__model_class == "ensemble-storm":
            self.__status_ensemble_storm(model)
        elif self.__model_class == "track":
            self.__status_track(model)
        else:
            raise RuntimeError("Unknown model type.")

    def __add_url_start_end_parameters(self, url):
        """
        This method is used to add the start and end parameters to the url

        Args:
            url: The url to add the start and end parameters to

        Returns:
            The url with the start and end parameters added
        """
        from datetime import datetime

        if self.__args.start:
            url += "&start={:s}".format(self.__args.start.strftime("%Y-%m-%d"))
            if not self.__args.end:
                url += "&end={:s}".format(datetime.utcnow().strftime("%Y-%m-%d"))
            else:
                url += "&end={:s}".format(self.__args.end.strftime("%Y-%m-%d"))
        return url

    def __status_track(self, model: str) -> None:
        """
        This method is used to get the status of the track data (NHC)

        Args:
            model: The model to get the status for
        """
        import requests
        import prettytable
        import json

        url = "{:s}/status?model={:s}".format(self.__environment["endpoint"], model)
        url = self.__add_url_start_end_parameters(url)
        if self.__args.storm:
            url += "&storm={:s}".format(self.__args.storm)
        if self.__args.basin:
            url += "&basin={:s}".format(self.__args.basin)

        response = requests.get(
            url, headers={"x-api-key": self.__environment["apikey"]}
        )
        data = response.json()["body"]

        if self.__args.format == "json":
            print(json.dumps(data))
        elif self.__args.format == "pretty":
            storm_tracks = []
            for year in data["best_track"].keys():
                for basin in data["best_track"][year].keys():
                    for storm in data["best_track"][year][basin]:
                        start_time = data["best_track"][year][basin][storm][
                            "best_track_start"
                        ]
                        end_time = data["best_track"][year][basin][storm][
                            "best_track_end"
                        ]
                        duration = data["best_track"][year][basin][storm]["duration"]

                        if year in data["forecast"].keys():
                            if basin in data["forecast"][year].keys():
                                if storm in data["forecast"][year][basin].keys():
                                    advisories = list(
                                        data["forecast"][year][basin][storm].keys()
                                    )
                                else:
                                    advisories = []
                            else:
                                advisories = []
                        else:
                            advisories = []
                        storm_tracks.append(
                            {
                                "year": year,
                                "basin": basin,
                                "storm": storm,
                                "start_time": start_time,
                                "end_time": end_time,
                                "duration": duration,
                                "advisories": advisories,
                            }
                        )
            table = prettytable.PrettyTable(
                [
                    "Year",
                    "Basin",
                    "Storm",
                    "Best Track Start",
                    "Best Track End",
                    "Duration (hrs)",
                    "Forecast Advisories",
                ]
            )
            for storm_track in storm_tracks:
                advisories = storm_track["advisories"]
                if len(advisories) > 6:
                    advisories = advisories[:3] + ["..."] + advisories[-3:]
                elif len(advisories) == 0:
                    advisories = ["None"]

                # ...Convert the list to a string
                advisories = " ".join(advisories)

                table.add_row(
                    [
                        storm_track["year"],
                        storm_track["basin"],
                        storm_track["storm"],
                        storm_track["start_time"],
                        storm_track["end_time"],
                        storm_track["duration"],
                        advisories,
                    ]
                )
            table.reversesort = True
            print(table.get_string(sortby="Best Track End"))

        else:
            raise RuntimeError("Unknown format")

    def __status_ensemble_storm(self, model: str) -> None:
        """
        This method is used to get the status of the ensemble storm data

        Args:
            model: The model to get the status for

        Returns:
            None
        """
        import requests
        import prettytable
        import json

        url = "{:s}/status?model={:s}".format(self.__environment["endpoint"], model)
        url = self.__add_url_start_end_parameters(url)
        if self.__args.storm:
            url += "&storm={:s}".format(self.__args.storm)
            if self.__args.ensemble_member:
                url += "&member={:s}".format(self.__args.ensemble_member)

        response = requests.get(
            url, headers={"x-api-key": self.__environment["apikey"]}
        )
        data = response.json()["body"]

        if self.__args.format == "json":
            print(json.dumps(data))
        elif self.__args.format == "pretty":
            if self.__args.storm and self.__args.ensemble_member:
                model_name = "{:s}-{:s}-{:s}".format(
                    model, self.__args.storm, self.__args.ensemble_member
                )
                self.__print_status_generic(
                    model_name, data[self.__args.storm][self.__args.ensemble_member]
                )
            else:

                table = prettytable.PrettyTable(
                    [
                        "Storm",
                        "First Forecast Cycle",
                        "Last Forecast Cycle",
                        "Earliest Forecast Time",
                        "Latest Forecast Time",
                        "Cycle Count",
                        "Ensemble Members",
                    ]
                )

                for storm in data.keys():
                    ensemble_members = []
                    for ensemble_member in data[storm].keys():
                        ensemble_members.append(ensemble_member)
                    table.add_row(
                        [
                            storm,
                            data[storm][ensemble_members[0]]["first_available_cycle"],
                            data[storm][ensemble_members[0]]["latest_available_cycle"],
                            data[storm][ensemble_members[0]]["min_forecast_date"],
                            data[storm][ensemble_members[0]]["max_forecast_date"],
                            len(data[storm][ensemble_members[0]]["cycles"]),
                            ensemble_members,
                        ]
                    )
                print(table)

    def __status_ensemble(self, model: str) -> None:
        """
        This method is used to get the status of the ensemble data

        Args:
            model: The model to get the status for

        Returns:
            None
        """
        import requests

        url = "{:s}/status?model={:s}".format(self.__environment["endpoint"], model)
        url = self.__add_url_start_end_parameters(url)
        if self.__args.ensemble_member:
            url += "&member={:s}".format(self.__args.ensemble_member)
        response = requests.get(
            url, headers={"x-api-key": self.__environment["apikey"]}
        )

        if self.__args.ensemble_member:
            model_name = "{:s}-{:s}".format(model, self.__args.ensemble_member)
            self.__print_status_generic(
                model_name, response.json()["body"][self.__args.ensemble_member]
            )
        else:
            self.__print_status_multi("ensemble", model, response.json()["body"])

    def __status_synoptic(self, model: str) -> None:
        """
        This method is used to get the status of the synoptic data

        Args:
            model: The model to get the status for

        Returns:
            None
        """
        import requests

        url = "{:s}/status?model={:s}".format(self.__environment["endpoint"], model)
        url = self.__add_url_start_end_parameters(url)

        # ...Get the json from the endpoint
        response = requests.get(
            url, headers={"x-api-key": self.__environment["apikey"]}
        )

        self.__print_status_generic(model.upper(), response.json()["body"])

    def __status_synoptic_storm(self, model: str) -> None:
        """
        This method is used to get the status of the synoptic data for storms

        Args:
            model: The model to get the status for

        Returns:
            None
        """
        import requests

        url = "{:s}/status?model={:s}".format(self.__environment["endpoint"], model)
        url = self.__add_url_start_end_parameters(url)

        if self.__args.storm:
            url += "&storm={:s}".format(self.__args.storm)

        # ...Get the json from the endpoint
        response = requests.get(
            url, headers={"x-api-key": self.__environment["apikey"]}
        )

        # ...Print
        if response.json()["body"] == {}:
            print("No data found")
        else:
            self.__print_status_multi("storm", model, response.json()["body"])

    def __print_status_multi(self, data_type: str, model: str, data: dict) -> None:
        """
        This method is used to print the status of the storm data

        Args:
            model: The model to get the status for
            data: The data to print the status for

        Returns:
            None
        """
        import prettytable
        import json

        if self.__args.format == "json":
            print(json.dumps(data))
        elif self.__args.format == "pretty":
            if data == {}:
                print("No data found.")
                return

            if self.__args.storm:
                model_name = "{:s}-{:s}".format(model.upper(), self.__args.storm)
                self.__print_status_generic(model_name, data[self.__args.storm])
            else:
                if data_type == "ensemble":
                    table = prettytable.PrettyTable(
                        [
                            "Ensemble Member",
                            "First Forecast Cycle",
                            "Last Forecast Cycle",
                            "Earliest Forecast Time",
                            "Latest Forecast Time",
                            "Cycle Count",
                        ]
                    )
                    table.align["Ensemble Member"] = "r"
                elif data_type == "storm":
                    table = prettytable.PrettyTable(
                        [
                            "Storm",
                            "First Forecast Cycle",
                            "Last Forecast Cycle",
                            "Earliest Forecast Time",
                            "Latest Forecast Time",
                            "Cycle Count",
                        ]
                    )
                    table.align["Storm"] = "r"
                else:
                    raise ValueError("Unknown data type: {:s}".format(data_type))

                for it in data.keys():
                    table.add_row(
                        [
                            it,
                            data[it]["first_available_cycle"],
                            data[it]["latest_available_cycle"],
                            data[it]["min_forecast_date"],
                            data[it]["max_forecast_date"],
                            len(data[it]["cycles"]),
                        ]
                    )
                table.align["Cycle Count"] = "r"

                if data_type == "ensemble":
                    print(
                        "Status for {:s} Model Ensemble Members".format(model.upper())
                    )
                    print(table.get_string(sortby="Ensemble Member"))
                elif data_type == "storm":
                    table.reversesort = True
                    print(
                        "Status for {:s} Model Storms (class: {:s})".format(
                            model.upper(), self.__model_class
                        )
                    )
                    print(table.get_string(sortby="First Forecast Cycle"))

    def __print_status_generic(self, model: str, data: dict) -> None:
        """
        This method is used to get the status of a generic format

        Args:
            model: The model to get the status for
            data: The data to get the status for

        Returns:
            None
        """
        import prettytable
        from datetime import datetime, timedelta
        import json

        if self.__args.format == "json":
            print(json.dumps(data))
        elif self.__args.format == "pretty":

            complete_cycles = data["cycles_complete"]

            print(
                "Status for model: {:s} (class: {:s})".format(model, self.__model_class)
            )
            table = prettytable.PrettyTable(["Forecast Cycle", "End Time", "Status"])

            for cycle in data["cycles"]:
                if cycle["cycle"] in complete_cycles:
                    status = "complete"
                else:
                    status = "incomplete ({:d})".format(cycle["duration"])
                table.add_row(
                    [
                        cycle["cycle"],
                        datetime.strptime(cycle["cycle"], "%Y-%m-%d %H:%M:%S")
                        + timedelta(hours=cycle["duration"]),
                        status,
                    ]
                )

            print(table)


def metget_status(args: argparse.Namespace) -> None:
    """
    This method is used to get the status of the metget data

    Args:
        args: The arguments passed to the command line

    Returns:
        None
    """
    s = MetGetStatus(args)
    return s.get_status()
