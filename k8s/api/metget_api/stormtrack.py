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
from typing import Tuple, Union

import flask


class StormTrackQueryStringParameters:
    """
    This class is used to parse the query string parameters for the storm track endpoint
    """

    def __init__(self, request: flask.Request):
        """
        Constructor for StormTrackQuery class

        Args:
            request: A flask request object
        """
        self.__year = None
        self.__basin = None
        self.__storm = None
        self.__advisory = None
        self.__type = None
        self.__valid = False
        self.__error_message = None
        self.__parse_request(request)

    def valid(self) -> bool:
        """
        Checks if the query string parameters are valid

        Returns:
            True if the query string parameters are valid, False otherwise
        """
        return self.__valid

    def error_message(self) -> str:
        """
        Returns the error message if the query string parameters are invalid

        Returns:
            The error message if the query string parameters are invalid
        """
        return self.__error_message

    def year(self) -> str:
        """
        Returns the year query string parameter

        Returns:
            The year query string parameter
        """
        return self.__year

    def basin(self) -> str:
        """
        Returns the basin query string parameter

        Returns:
            The basin query string parameter
        """
        return self.__basin

    def storm(self) -> str:
        """
        Returns the storm query string parameter

        Returns:
            The storm query string parameter
        """
        return self.__storm

    def advisory(self) -> Union[str, None]:
        """
        Returns the advisory query string parameter if the track type is forecast

        Returns:
            The advisory query string parameter or None if the track type is best
        """
        if self.__type == "best":
            return None
        return self.__advisory

    def type(self) -> str:
        """
        Returns the type query string parameter

        Returns:
            The type query string parameter
        """
        return self.__type

    def __parse_request(self, request: flask.Request):
        """
        Parses the query string parameters from the request

        Args:
            request: A flask request object

        Returns:
            None
        """
        if "year" in request.args:
            self.__year = request.args["year"]
        else:
            self.__error_message = "Query string parameter 'year' not provided"
            return

        if "basin" in request.args:
            self.__basin = request.args["basin"]
        else:
            self.__error_message = "Query string parameter 'basin' not provided"

        if "storm" in request.args:
            self.__storm = request.args["storm"]
        else:
            self.__error_message = "Query string parameter 'storm' not provided"

        if "type" in request.args:
            self.__type = request.args["type"]
            if self.__type != "best" and self.__type != "forecast":
                self.__error_message = "Invalid track type specified: {:s}".format(
                    self.__type
                )
        else:
            self.__error_message = "Query string parameter 'type' not provided"

        if self.__type == "forecast":
            if "advisory" in request.args:
                advisory_str = request.args["advisory"]
                try:
                    advisory_int = int(advisory_str)
                    self.__advisory = "{:03d}".format(advisory_int)
                except ValueError:
                    self.__advisory = advisory_str
            else:
                self.__error_message = "Query string parameter 'advisory' not provided"

        self.__valid = True


class StormTrack:
    """
    This class is used to query the NHC storm track data from MetGet
    """

    def __init__(self):
        """
        Constructor for StormTrack class
        """
        pass

    @staticmethod
    def get(request: flask.Request) -> Tuple[dict, int]:
        """
        This method is used to query the NHC storm track data from MetGet

        Args:
            request: A flask request object

        Returns:
            A tuple containing the response message and status code
        """

        query = StormTrackQueryStringParameters(request)

        return_message = {
            "body": {
                "query": {
                    "type": query.type(),
                    "advisory": query.advisory(),
                    "basin": query.basin(),
                    "storm": query.storm(),
                    "year": query.year(),
                },
            },
        }

        if not query.valid():
            status_code = 400
            return_message["body"]["message"] = query.error_message()
            return return_message, status_code

        if query.type() == "forecast":
            query_result = StormTrack.__get_forecast_track(query)
        else:
            query_result = StormTrack.__get_best_track(query)

        if len(query_result) == 0:
            status_code = 400
            return_message["body"]["message"] = "ERROR: No data found to match request"
        elif len(query_result) > 1:
            status_code = 400
            return_message["body"][
                "message"
            ] = "ERROR: Too many records found matching request"
        else:
            status_code = 200
            return_message["body"]["message"] = "Success"
            return_message["body"]["geojson"] = query_result[0][0]

        return_message["statusCode"] = status_code
        return return_message, status_code

    @staticmethod
    def __get_best_track(query: StormTrackQueryStringParameters):
        """
        This method is used to query the NHC best track data from MetGet

        Args:
            query: A StormTrackQuery object

        Returns:
            GEOJSON data for the best track
        """

        from metbuild.tables import NhcBtkTable
        from metbuild.database import Database

        with Database() as db, db.session() as session:
            query = session.query(NhcBtkTable.geometry_data).filter(
                NhcBtkTable.storm_year == query.year(),
                NhcBtkTable.basin == query.basin(),
                NhcBtkTable.storm == query.storm(),
            )
        return query.all()

    @staticmethod
    def __get_forecast_track(query: StormTrackQueryStringParameters):
        """
        This method is used to query the NHC forecast track data from MetGet

        Args:
            query: A StormTrackQuery object

        Returns:
            GEOJSON data for the forecast track
        """

        from metbuild.tables import NhcFcstTable
        from metbuild.database import Database

        with Database() as db, db.session() as session:
            query = session.query(NhcFcstTable.geometry_data).filter(
                NhcFcstTable.storm_year == query.year(),
                NhcFcstTable.basin == query.basin(),
                NhcFcstTable.storm == query.storm(),
                NhcFcstTable.advisory == query.advisory(),
            )
        return query.all()
