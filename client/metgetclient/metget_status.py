#!/usr/bin/env python3
################################################################################
# MetGet Client
#
# This file is part of the MetGet distribution (https://github.com/waterinstitute/metget).
# Copyright (c) 2023, The Water Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Zach Cobell, zcobell@thewaterinstitute.org
#
################################################################################
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
                url += "&end={:s}".format(self.__args.end)
        return url

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

        if self.__args.format == "json":
            print(data)
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

        if self.__args.format == "json":
            print(data)
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
