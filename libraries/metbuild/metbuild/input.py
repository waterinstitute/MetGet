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

from datetime import datetime

VALID_DATA_TYPES = ["wind_pressure", "rain", "ice", "humidity", "temperature"]


class Input:
    """
    This class is used to parse the input JSON data and validate it
    for use in the MetBuild process
    """

    def __init__(self, json_data, no_construct: bool = False):
        """
        Constructor for Input

        Args:
            json_data: A dictionary containing the json data for the input

        """
        self.__json = json_data
        self.__data_type = "wind_pressure"
        self.__no_construct = no_construct
        self.__start_date = None
        self.__end_date = None
        self.__operator = None
        self.__version = None
        self.__filename = None
        self.__format = None
        self.__time_step = None
        self.__nowcast = False
        self.__backfill = False
        self.__strict = False
        self.__multiple_forecasts = True
        self.__valid = True
        self.__dry_run = False
        self.__compression = False
        self.__epsg = 4326
        self.__request_id = None
        self.__error = []
        self.__domains = []
        self.__parse()
        self.__credit_usage = self.__calculate_credit_usage()

    def request_id(self) -> str:
        """
        Returns the request id

        Returns:
            The request id
        """
        return self.__request_id

    def credit_usage(self) -> int:
        """
        Returns the credit cost of the request

        Returns:
            The credit cost of the request
        """
        return self.__credit_usage

    def valid(self):
        """
        Returns whether the input is valid

        Returns:
            A boolean indicating whether the input is valid
        """
        return self.__valid

    def epsg(self) -> int:
        """
        Returns the epsg projection code that the user
        requested the data be returned in

        Returns:
            epsg code of output data
        """
        return self.__epsg

    def data_type(self) -> str:
        """
        Returns the data type that has been requested

        Returns:
            data type requested by the user request
        """
        return self.__data_type

    def dry_run(self):
        """
        Returns whether the input is a dry run

        Returns:
            A boolean indicating whether the input is a dry run
        """
        return self.__dry_run

    def compression(self) -> bool:
        """
        Returns the option for using ascii file compression in output

        Returns:
            boolean indicating if compression should be turned on/off
        """
        return self.__compression

    def error(self) -> list:
        """
        Returns the error message

        Returns:
            The error message
        """
        return self.__error

    def format(self):
        """
        Returns the format of the output data requested

        Returns:
            The format of the output data requested
        """
        return self.__format

    def filename(self):
        """
        Returns the filename that will be used for the output data

        Returns:
            The filename that will be used for the output data
        """
        return self.__filename

    def json(self):
        """
        Returns the json data that was provided in the input

        Returns:
            The json data that was provided in the input
        """
        return self.__json

    def version(self):
        """
        Returns the version of the input data

        Returns:
            The version of the input data
        """
        return self.__version

    def operator(self):
        """
        Returns the operator who provided the input data

        Returns:
            The operator who provided the input data
        """
        return self.__operator

    @staticmethod
    def date_to_pmb(date: datetime):
        """
        Converts a date into the pymetbuild date object

        Args:
            datetime object

        Returns:
            pymetbuild.Date object
        """
        import pymetbuild

        return pymetbuild.Date(date.year, date.month, date.day, date.hour, date.minute)

    def start_date_pmb(self):
        """
        Returns the start date as a pymetbuild object

        Returns:
            start date as a pymetbuild object
        """
        return Input.date_to_pmb(self.__start_date)

    def end_date_pmb(self):
        """
        Returns the end date as a pymetbuild object

        Returns:
            end date as a pymetbuild object
        """
        return Input.date_to_pmb(self.__end_date)

    def start_date(self):
        """
        Returns the start date of the input data

        Returns:
            The start date of the input data
        """
        return self.__start_date

    def end_date(self):
        """
        Returns the end date of the input data

        Returns:
            The end date of the input data
        """
        return self.__end_date

    def time_step(self):
        """
        Returns the time step of the input data

        Returns:
            The time step of the input data
        """
        return self.__time_step

    def num_domains(self):
        """
        Returns the number of domains in the input data

        Returns:
            The number of domains in the input data
        """
        return len(self.__domains)

    def domain(self, index):
        """
        Returns the domain at the specified index

        Args:
            index: The index of the domain to return
        """
        return self.__domains[index]

    def nowcast(self):
        """
        Returns whether the data should only contain nowcast data

        Returns:
            A boolean indicating whether the data should only contain nowcast data
        """
        return self.__nowcast

    def multiple_forecasts(self):
        """
        Returns whether the output data should contain multiple forecasts

        Returns:
            A boolean indicating whether the output data should contain multiple forecasts
        """
        return self.__multiple_forecasts

    def backfill(self):
        """
        Returns whether the output data should be backfilled when the domain
        extents are not available

        Returns:
            A boolean indicating whether the output data should be backfilled
        """
        return self.__backfill

    def strict(self):
        """
        Returns whether the request should be handled strictly

        Returns:
            A boolean indicating whether the request should be handled strictly
        """
        return self.__strict

    def __parse(self):
        """
        Parses the input data
        """
        import dateutil.parser
        from .domain import Domain

        try:
            self.__version = self.__json["version"]
            self.__operator = self.__json["creator"]
            self.__request_id = self.__json["request_id"]
            self.__start_date = dateutil.parser.parse(self.__json["start_date"])
            self.__start_date = self.__start_date.replace(tzinfo=None)
            self.__end_date = dateutil.parser.parse(self.__json["end_date"])
            self.__end_date = self.__end_date.replace(tzinfo=None)
            self.__time_step = self.__json["time_step"]
            self.__filename = self.__json["filename"]
            self.__format = self.__json["format"]

            if self.__format == "owi-netcdf" or self.__format == "hec-netcdf":
                if not self.__filename[-3:-1] == "nc":
                    self.__filename = self.__filename + ".nc"

            if "data_type" in self.__json.keys():
                self.__data_type = self.__json["data_type"]
                if self.__data_type not in VALID_DATA_TYPES:
                    raise RuntimeError("Invalid data type specified")

            if "dry_run" in self.__json.keys():
                self.__dry_run = self.__json["dry_run"]

            if "compression" in self.__json.keys():
                self.__compression = self.__json["compression"]

            if "backfill" in self.__json.keys():
                self.__backfill = self.__json["backfill"]

            if "epsg" in self.__json.keys():
                self.__epsg = self.__json["epsg"]

            if "nowcast" in self.__json.keys():
                self.__nowcast = self.__json["nowcast"]

            if "multiple_forecasts" in self.__json.keys():
                self.__multiple_forecasts = self.__json["multiple_forecasts"]

            if "strict" in self.__json.keys():
                self.__strict = self.__json["strict"]

            # ... Sanity check
            if self.__start_date >= self.__end_date:
                self.__error.append("Request dates are not valid")
                self.__valid = False

            ndomain = len(self.__json["domains"])
            if ndomain == 0:
                raise RuntimeError("You must specify one or more wind domains")
            for i in range(ndomain):
                name = self.__json["domains"][i]["name"]
                service = self.__json["domains"][i]["service"]
                d = Domain(
                    name, service, self.__json["domains"][i], self.__no_construct
                )
                if d.valid():
                    self.__domains.append(d)
                else:
                    self.__valid = False
                    self.__error.append("Could not generate domain " + str(i))

        except Exception as e:
            self.__valid = False
            self.__error.append("Could not parse the input json dataset: " + str(e))

    def __calculate_credit_usage(self) -> int:
        """
        Calculates the credit usage of the request

        Credits are calculated as the number of grid cells
        multiplied by the number of time steps

        Returns:
            The credit usage of the request
        """
        credit_usage = 0
        num_time_steps = int(
            (self.__end_date - self.__start_date).total_seconds() / self.__time_step
        )
        for d in self.__domains:
            if d.service() != "nhc" and self.format() != "raw":
                num_cells = d.grid().nx() * d.grid().ny()
                credit_usage += num_cells * num_time_steps
            else:
                if d.service() == "nhc":
                    credit_usage += 100 * 100 * 24
                else:
                    credit_usage += 100 * 100 * 24 * num_time_steps
        return credit_usage
