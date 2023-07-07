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


def metget_version() -> str:
    """
    This method is used to get the version of the MetGet client

    Returns:
        The version of the MetGet client
    """
    from . import __version__ as version

    return version


def get_metget_environment_variables(args: argparse.Namespace) -> dict:
    """
    This method is used to get the environment variables for the endpoint and
    apikey

    Args:
        args: The arguments passed to the command line

    Returns:
        A dictionary containing the endpoint and apikey
    """
    import os

    if not args.endpoint:
        if "METGET_ENDPOINT" not in os.environ:
            raise RuntimeError("No endpoint found.")
        else:
            endpoint = os.environ["METGET_ENDPOINT"]
    else:
        endpoint = args.endpoint

    if not args.apikey:
        if "METGET_API_KEY" not in os.environ:
            raise RuntimeError("No API key was found.")
        else:
            apikey = os.environ["METGET_API_KEY"]
    else:
        apikey = args.apikey

    if not args.api_version:
        if "METGET_API_VERSION" not in os.environ:
            api_version = 1
        else:
            api_version = int(os.environ["METGET_API_VERSION"])
    else:
        api_version = args.api_version

    return {"endpoint": endpoint, "apikey": apikey, "api_version": api_version}
