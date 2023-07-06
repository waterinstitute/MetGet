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

# Available metget models
AVAILABLE_MODELS = {
    "gfs": "gfs-ncep",
    "gefs": "gefs-ncep",
    "nam": "nam-ncep",
    "hwrf": "hwrf",
    "hrrr": "hrrr-conus",
    "hrrr-alaska": "hrrr-alaska",
    "wpc": "wpc-ncep",
    "coamps": "coamps-tc",
    "ctcx": "coamps-ctcx",
    "nhc": "nhc",
}

# Available metget model types
MODEL_TYPES = {
    "gfs": "synoptic",
    "gefs": "ensemble",
    "nam": "synoptic",
    "hwrf": "synoptic-storm",
    "hrrr": "synoptic",
    "hrrr-alaska": "synoptic",
    "wpc": "synoptic",
    "coamps": "synoptic-storm",
    "ctcx": "ensemble-storm",
    "nhc": "track",
}

# Available metget variables
AVAILABLE_VARIABLES = {"wind_pressure", "rain", "temperature", "humidity", "ice"}

# Available metget formats
AVAILABLE_FORMATS = {
    "raw": "raw",
    "ascii": "ascii",
    "owi-ascii": "owi-ascii",
    "owi-netcdf": "owi-netcdf",
    "hec-netcdf": "hec-netcdf",
    "generic-netcdf": "hec-netcdf",
    "delft3d": "delft3d",
}


def get_metget_available_model_list() -> str:
    """
    This method is used to return a comma separated list of available models

    Returns:
        A comma separated list of available models
    """
    mlist = str()
    for m in AVAILABLE_MODELS.keys():
        if len(mlist) == 0:
            mlist += m
        else:
            mlist += ", " + m
    return mlist
