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


class MetGetTrack:
    """
    This class is used to generate a MetGet track data from the api
    """

    def __init__(self, args: argparse.Namespace):
        from .metget_environment import get_metget_environment_variables

        self.__args = args
        self.__environment = get_metget_environment_variables(args)

    def get_track(self):
        """
        This method is used to get the track data from the api
        """
        import requests
        from datetime import datetime
        import json

        url = self.__environment["endpoint"] + "/stormtrack"

        if not self.__args.storm:
            raise ValueError("Storm must be specified for track data")

        if not self.__args.type:
            raise ValueError("Type must be specified for track data")

        # ...Default basin is Atlantic
        if not self.__args.basin:
            self.__args.basin = "al"

        # ...Default year is the current year
        if not self.__args.year:
            self.__args.year = datetime.now().year

        storm_id = "{:02d}".format(int(self.__args.storm))

        if self.__args.type == "besttrack":
            params = {
                "type": "best",
                "storm": storm_id,
                "basin": self.__args.basin,
                "year": self.__args.year,
            }
        elif self.__args.type == "forecast":
            if not self.__args.advisory:
                raise ValueError("Advisory must be specified for forecast track data")

            advisory_id = "{:03d}".format(int(self.__args.advisory))
            params = {
                "type": "forecast",
                "storm": storm_id,
                "basin": self.__args.basin,
                "advisory": advisory_id,
                "year": self.__args.year,
            }
        else:
            raise ValueError("Type must be besttrack or forecast")

        # Get the track data with the requests library
        response = requests.get(url, params=params)

        # Check the response status code
        if response.status_code == 200:
            print(json.dumps(response.json()["body"]["geojson"]))
        else:
            print("Error: {}".format(response.status_code))
            print(json.dumps(response.json()))


def metget_track(args: argparse.Namespace) -> None:
    """
    This method is used to get the track data from the api

    Args:
        args: The command line arguments

    Returns:
        None
    """
    track = MetGetTrack(args)
    track.get_track()
