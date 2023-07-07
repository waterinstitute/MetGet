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
from typing import Tuple


class MetBuildRequest:
    """
    This class is used to build a new MetGet request into a 2d wind field
    """

    def __init__(self, api_key: str, source_ip: str, request_id: str, json_data: dict):
        """
        Constructor for BuildRequest

        Args:
            request_id: A string containing the request id
            api_key: A string containing the api key
            source_ip: A string containing the source ip
            json_data: A dictionary containing the json data for the request
        """
        import os

        self.__json_data = json_data
        self.__api_key = api_key
        self.__source_ip = source_ip
        self.__request_id = request_id
        self.__output_bucket = os.environ["METGET_S3_BUCKET_UPLOAD"]
        self.__build_request = None
        self.__error = []

        enforce_credit_limits = os.environ["METGET_ENFORCE_CREDIT_LIMITS"]
        if enforce_credit_limits.lower() == "true":
            self.__enforce_credit_limits = True
        else:
            self.__enforce_credit_limits = False

        self.__json_data["request_id"] = self.__request_id
        self.__json_data["api_key"] = self.__api_key
        self.__json_data["source_ip"] = self.__source_ip

    def generate_request(self) -> Tuple[dict, int]:
        """
        This method is used to add a new request to the database and initiate
        the k8s process within argo

        Returns:
            A tuple containing the response message and status code
        """
        from metget_api.build_request import BuildRequest
        from metbuild.tables import RequestEnum

        self.__build_request = BuildRequest(
            self.__request_id, self.__api_key, self.__source_ip, self.__json_data, True
        )

        statuscode = 200
        msg = {
            "statusCode": 200,
            "body": {
                "status": "empty",
                "message": "empty",
                "request_id": "empty",
                "request_url": "empty",
                "credits": {},
                "error_text": [],
            },
        }

        valid = self.__build_request.validate()
        if valid:

            credit_dict, credit_balance_authorized = self.__generate_credit_info(
                self.__api_key,
                self.__build_request.input_obj().credit_usage(),
            )

            if self.__build_request.input_obj().dry_run():
                msg["body"]["status"] = "success"
                msg["body"]["message"] = "dry run successful"
                msg["body"]["request_id"] = self.__build_request.request_id()
                msg["body"]["request_url"] = "n/a"
                msg["body"]["credits"] = credit_dict
                msg["body"]["error_text"] = []
            else:
                if credit_balance_authorized or (not self.__enforce_credit_limits):
                    msg["body"]["status"] = "success"
                    msg["body"]["message"] = "Request added to queue"
                    msg["body"]["request_id"] = self.__build_request.request_id()
                    msg["body"][
                        "request_url"
                    ] = "https://{:s}.s3.amazonaws.com/{:s}".format(
                        self.__output_bucket, self.__build_request.request_id()
                    )
                    msg["body"]["credits"] = credit_dict
                    msg["body"]["error_text"] = []

                    self.__build_request.add_request(
                        RequestEnum.queued,
                        "Request added to queue",
                        True,
                        self.__build_request.input_obj().credit_usage(),
                    )
                else:
                    statuscode = 402
                    msg["statusCode"] = 402
                    msg["body"]["status"] = "error"
                    msg["body"]["message"] = "Insufficient credits"
                    msg["body"]["request_id"] = self.__build_request.request_id()
                    msg["body"]["request_url"] = "n/a"
                    msg["body"]["credits"] = credit_dict
                    msg["body"]["error_text"] = []
        else:
            msg["statusCode"] = 401
            msg["body"]["status"] = "error"
            msg["body"]["message"] = "Request could not be added to queue"
            msg["body"]["request_id"] = self.__build_request.request_id()
            msg["body"]["request_url"] = "n/a"
            msg["body"]["error_text"] = self.__build_request.error()

        return msg, statuscode

    @staticmethod
    def __generate_credit_info(
        api_key: str, credit_usage_request: int
    ) -> Tuple[dict, bool]:
        """
        This method is used to generate the credit information for the request
        and check if the request is authorized based on the credit balance

        Args:
            api_key: A string containing the api key
            credit_usage_request: An integer containing the credit usage for the request

        Returns:
            A tuple containing the credit information and a boolean indicating if the request is authorized
        """
        from metget_api.access_control import AccessControl

        credit_dict = AccessControl.get_credit_balance(api_key)

        credit_balance = credit_dict["credit_balance"] - credit_usage_request
        credit_limit = credit_dict["credit_limit"]
        credit_usage = credit_dict["credits_used"] + credit_usage_request

        if credit_limit == 0:
            credit_balance = 0
            authorized = True
        elif credit_balance <= 0:
            authorized = False
        else:
            authorized = True

        return {
            "credit_usage_request": credit_usage_request,
            "credit_usage_total": credit_usage,
            "credit_limit": credit_limit,
            "credit_balance": credit_balance,
        }, authorized
