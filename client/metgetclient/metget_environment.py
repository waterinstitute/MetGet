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
