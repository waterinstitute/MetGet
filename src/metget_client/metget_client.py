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


def initialize_build_cli(subparsers):
    """
    This method is used to initialize the build subparser

    Args:
        subparsers: The build subparser

    Returns:
        None
    """
    from datetime import datetime
    from .metget_build import metget_build
    from .metget_data import get_metget_available_model_list

    build = subparsers.add_parser(
        name="build",
        help="Generate a MetGet build request",
    )
    build.set_defaults(func=metget_build)

    mlist = get_metget_available_model_list()
    build.add_argument(
        "--domain",
        help="Wind domain specification. Model may be any of ["
        + mlist
        + "]. Resolution and corners are decimal degrees"
        " For HWRF/COAMPS, the model can be listed as 'hwrf-[stormname]' or 'coamps-[stormname]'."
        " For GEFS, the ensemble member can be specified as 'gefs-[ensemble_member]'. For NHC data"
        " specify as 'nhc-basin-storm_number-advisory_number' where basin is a two letter string denoting"
        " the basin (al, ep, wp), storm number is the id of the storm (not the name), and the advisory number"
        " is the advisory to use to build the merged data (or 0 for best-track data only).",
        nargs=6,
        metavar=("model", "resolution", "x0", "y0", "x1", "y1"),
        action="append",
    )
    build.add_argument(
        "--start",
        help="Start time",
        type=datetime.fromisoformat,
        metavar="YYYY-MM-DD hh:mm",
    )
    build.add_argument(
        "--end",
        help="End time",
        type=datetime.fromisoformat,
        metavar="YYYY-MM-DD hh:mm",
    )
    build.add_argument(
        "--timestep", help="Time step of winds in seconds", metavar="dt", type=int
    )
    build.add_argument(
        "--analysis", help="Generate analysis wind fields", action="store_true"
    )
    build.add_argument(
        "--multiple-forecasts",
        help="Allow the use of multiple forecast wind fields",
        action="store_true",
    )
    build.add_argument(
        "--initialization-skip",
        help="For COAMPS-TC, skip some initialization period of each forecast. "
        "This is considered a discard period where forecast times < [skip] hours are "
        "discarded when selecting the data",
        type=int,
        metavar="h",
        required=False,
        default=0,
    )
    build.add_argument(
        "--output", help="Base name of output data", type=str, metavar="s"
    )
    build.add_argument(
        "--format",
        help="Output format (raw, owi-ascii, owi-netcdf, generic-netcdf (hec-netcdf), delft3d)",
        metavar="f",
        default="owi-ascii",
    )
    build.add_argument(
        "--variable",
        help="Variable to request from MetGet (wind_pressure, rain, humidity, temperature, ice)",
        metavar="v",
        default="wind_pressure",
    )
    build.add_argument(
        "--check-interval",
        help="Time between status checks (default=10s)",
        metavar="t",
        default=10,
        type=float,
    )
    build.add_argument(
        "--max-wait",
        help="Maximum wait time for the request to complete in hours (default=24)",
        metavar="h",
        default=24,
        type=float,
    )
    build.add_argument(
        "--strict",
        action="store_true",
        help="Do not allow MetGet to make due with what it has. Force the response to match the request",
    )
    build.add_argument(
        "--backfill",
        action="store_true",
        help="Backfill data from lower priority domains",
        default=False,
    )
    build.add_argument(
        "--epsg",
        help="Coordinate system of the specified domain and output data (default: 4326)",
        required=False,
        metavar="#",
        type=int,
        default=4326,
    )
    build.add_argument("--dryrun", help="Perform dry run only", action="store_true")
    build.add_argument(
        "--request",
        help="Check on and download specified request id",
        type=str,
        metavar="request_id",
    )
    build.add_argument(
        "--compression",
        action="store_true",
        help="For ASCII based data formats, use gzip compression in the retreived files",
        default=False,
    )
    build.add_argument(
        "--save-json-request",
        action="store_true",
        help="Save the json request sent to the MetGet API as request.json",
        default=False,
    )


def initialize_credits_cli(subparsers):
    """
    This method is used to initialize the credits subparser

    Args:
        subparsers: The credits subparser

    Returns:
        None
    """
    from .metget_credits import metget_credits

    api_credits = subparsers.add_parser(
        "credits", help="Check the number of credits available"
    )
    api_credits.add_argument(
        "--format",
        help="Output format (json, pretty)",
        default="json",
        type=str,
    )
    api_credits.set_defaults(func=metget_credits)


def initialize_status_cli(subparsers):
    from datetime import datetime
    from .metget_status import metget_status
    from .metget_data import get_metget_available_model_list

    status = subparsers.add_parser(
        "status", help="Check the status of the available data"
    )
    status.set_defaults(func=metget_status)
    mlist = get_metget_available_model_list()
    status.add_argument(
        "model", help="Name of model to get status for (" + mlist + ")", type=str
    )
    status.add_argument(
        "--start",
        help="Earlier date to retrieve status for",
        type=datetime.fromisoformat,
        metavar="YYYY-MM-DD hh:mm",
    )
    status.add_argument(
        "--end",
        help="Later date to retrieve status for",
        type=datetime.fromisoformat,
        metavar="YYYY-MM-DD hh:mm",
    )
    status.add_argument(
        "--basin",
        help="For NHC based data, request a specific basin",
        type=str,
        metavar="s",
    )
    status.add_argument(
        "--storm",
        help="For storm based data, request a specific storm",
        type=str,
        metavar="s",
    )
    status.add_argument(
        "--ensemble-member",
        help="Ensemble member to request data for",
        type=str,
        metavar="s",
    )
    status.add_argument(
        "--format", help="Output format (json, pretty)", metavar="f", default="pretty"
    )


def initialize_track_cli(subparsers) -> None:
    """
    This method is used to initialize the track subparser

    Returns:
        None
    """
    from .metget_track import metget_track

    track = subparsers.add_parser(
        "track", help="Get the storm track data for a NHC storm"
    )
    track.set_defaults(func=metget_track)
    track.add_argument(
        "--year", help="NHC Storm year to get track data for", type=int, metavar="n"
    )
    track.add_argument(
        "--storm", help="NHC Storm number to get track data for", type=int, metavar="n"
    )
    track.add_argument(
        "--basin",
        help="NHC Storm basin to get track data for (al, ep, wp)",
        type=str,
        metavar="s",
        default="al",
    )
    track.add_argument(
        "--advisory", help="NHC Storm advisory to get", type=str, metavar="s"
    )
    track.add_argument(
        "--type",
        help="Type of track data to get (besttrack or forecast)",
        type=str,
        metavar="s",
    )


def metget_client_cli() -> None:
    """
    Main function for command line interface
    """
    import argparse
    from .metget_environment import metget_version

    p = argparse.ArgumentParser(
        description="Client for interaction with a MetGet API instance",
        prog="metget",
    )
    p.add_argument(
        "--version", action="version", version="%(prog)s " + metget_version()
    )
    p.add_argument(
        "--apikey", help="API key for access to MetGet", type=str, metavar="s"
    )
    p.add_argument("--endpoint", help="MetGet API endpoint", type=str, metavar="s")
    p.add_argument(
        "--api-version",
        type=int,
        help="MetGet API version. Default is 1. When using the k8s MetGet API, this should be 2.",
        metavar="n",
    )

    subparsers = p.add_subparsers(help="Sub-command help")
    initialize_build_cli(subparsers)
    initialize_status_cli(subparsers)
    initialize_track_cli(subparsers)
    initialize_credits_cli(subparsers)

    args = p.parse_args()
    if "func" in args:
        args.func(args)
    else:
        p.print_help()


if __name__ == "__main__":
    metget_client_cli()
