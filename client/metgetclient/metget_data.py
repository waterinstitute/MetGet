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
