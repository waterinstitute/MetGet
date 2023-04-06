# !/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 ADCIRC Development Group
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

from datetime import datetime

VALID_DATA_TYPES = ["wind_pressure", "rain", "ice", "humidity", "temperature"]


class Input:
    """
    Class to parse the input json data
    """

    def __init__(self, json_data: dict):
        """
        Constructor for the Input class

        Args:
            json_data (dict): The input json data

        """
        import uuid

        self.__json = json_data
        self.__data_type = "wind_pressure"
        self.__start_date = None
        self.__end_date = None
        self.__operator = None
        self.__version = None
        self.__filename = None
        self.__format = None
        self.__time_step = None
        self.__nowcast = False
        self.__backfill = False
        self.__compression = False
        self.__epsg = 4326
        self.__multiple_forecasts = True
        self.__domains = []
        self.__parse()
        self.__uuid = str(uuid.uuid4())

    def uuid(self) -> str:
        """
        Returns the uuid of the input data
        """
        return self.__uuid

    def data_type(self) -> str:
        """
        Returns the data type of the input data
        """
        return self.__data_type

    def format(self) -> str:
        """
        Returns the format of the input data
        """
        return self.__format

    def filename(self) -> str:
        """
        Returns the filename of the input data
        """
        return self.__filename

    def json(self) -> dict:
        """
        Returns the json data
        """
        return self.__json

    def version(self) -> str:
        """
        Returns the version of the input data
        """
        return self.__version

    def operator(self) -> str:
        """
        Returns the operator of the input data
        """
        return self.__operator

    def start_date(self) -> datetime:
        """
        Returns the start date of the input data
        """
        return self.__start_date

    @staticmethod
    def date_to_pmb(date: datetime):
        """
        Converts a datetime object to a pymetbuild date object
        """
        import pymetbuild

        return pymetbuild.Date(date.year, date.month, date.day, date.hour, date.minute)

    def start_date_pmb(self):
        """
        Returns the start date of the input data in a pymetbuild date object
        """
        return Input.date_to_pmb(self.__start_date)

    def end_date(self):
        """
        Returns the end date of the input data
        """
        return self.__end_date

    def end_date_pmb(self):
        """
        Returns the end date of the input data in a pymetbuild date object
        """
        return Input.date_to_pmb(self.__end_date)

    def time_step(self):
        """
        Returns the time step of the input data in seconds
        """
        return self.__time_step

    def num_domains(self):
        """
        Returns the number of domains
        """
        return len(self.__domains)

    def domain(self, index: int):
        """
        Returns the domain at the specified index
        """
        return self.__domains[index]

    def nowcast(self):
        """
        Returns true if the input data is a nowcast
        """
        return self.__nowcast

    def multiple_forecasts(self):
        """
        Returns true if the input data is a multiple forecasts
        """
        return self.__multiple_forecasts

    def backfill(self):
        """
        Returns true if the output data uses backfill
        """
        return self.__backfill

    def compression(self):
        """
        Returns true if the output data should be compressed
        """
        return self.__compression

    def epsg(self):
        """
        Returns the epsg code of the input data
        """
        return self.__epsg

    def __parse(self):
        """
        Parses the input json data and sets the class variables
        """
        import sys
        import logging
        import dateutil.parser
        from metbuild.domain import Domain

        log = logging.getLogger(__name__)

        try:
            self.__version = self.__json["version"]
            self.__operator = self.__json["creator"]
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

            if "backfill" in self.__json.keys():
                self.__backfill = self.__json["backfill"]

            if "epsg" in self.__json.keys():
                self.__epsg = self.__json["epsg"]

            if "nowcast" in self.__json.keys():
                self.__nowcast = self.__json["nowcast"]

            if "multiple_forecasts" in self.__json.keys():
                self.__multiple_forecasts = self.__json["multiple_forecasts"]

            if "compression" in self.__json.keys():
                self.__compression = self.__json["compression"]

            ndomain = len(self.__json["domains"])
            if ndomain == 0:
                raise RuntimeError("You must specify one or more wind domains")
            for i in range(ndomain):
                name = self.__json["domains"][i]["name"]
                service = self.__json["domains"][i]["service"]
                self.__domains.append(Domain(name, service, self.__json["domains"][i]))
        except KeyError as e:
            log.error("Could not parse the input json dataset: ", e)
            raise RuntimeError("Could not parse the input json dataset: ", str(e))
