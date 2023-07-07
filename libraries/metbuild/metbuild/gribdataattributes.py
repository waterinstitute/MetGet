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
class GribDataAttributes:
    def __init__(
        self,
        name: str,
        table: str,
        bucket: str,
        variables: dict,
        cycles: list,
        ensemble_members: list = None,
    ):
        self.__name = name
        self.__table = table
        self.__bucket = bucket
        self.__cycles = cycles
        self.__ensemble_members = ensemble_members

        self.__variables = []
        for variable in variables.keys():
            self.__variables.append(
                {
                    "name": variable,
                    "long_name": variables[variable],
                }
            )

    def name(self) -> str:
        return self.__name

    def table(self) -> str:
        return self.__table

    def bucket(self) -> str:
        return self.__bucket

    def variables(self) -> dict:
        return self.__variables

    def cycles(self) -> list:
        return self.__cycles

    def ensemble_members(self) -> list:
        return self.__ensemble_members


NCEP_GFS = GribDataAttributes(
    "GFS-NCEP",
    "gfs_ncep",
    "noaa-gfs-bdp-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "ice": "ICEC:surface",
        "precip_rate": "PRATE",
        "humidity": "RH:30-0 mb above ground",
        "temperature": "TMP:30-0 mb above ground",
    },
    [0, 6, 12, 18],
)

NCEP_NAM = GribDataAttributes(
    "NAM-NCEP",
    "nam_ncep",
    "noaa-nam-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "accumulated_precip": "APCP",
        "humidity": "RH:30-0 mb above ground",
        "temperature": "TMP:30-0 mb above ground",
    },
    [0, 6, 12, 18],
)

NCEP_GEFS = GribDataAttributes(
    "GEFS-NCEP",
    "gefs_ncep",
    "noaa-gefs-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "ice": "ICETK:surface",
        "accumulated_precip": "APCP",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [0, 6, 12, 18],
    # ...GEFS ensemble members:
    #   Valid perturbations for gefs are:
    #   avg => ensemble mean
    #   c00 => control
    #   pXX => perturbation XX (1-30)
    ["avg", "c00", *[f"p{i:02d}" for i in range(1, 31)]],
)

NCEP_HRRR = GribDataAttributes(
    "HRRR-NCEP",
    "hrrr_ncep",
    "noaa-hrrr-bdp-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "MSLMA:mean sea level",
        "ice": "ICEC:surface",
        "precip_rate": "PRATE",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [i for i in range(0, 24)],
)

NCEP_HRRR_ALASKA = GribDataAttributes(
    "HRRR-ALASKA-NCEP",
    "hrrr_alaska_ncep",
    "noaa-hrrr-bdp-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "MSLMA:mean sea level",
        "ice": "ICEC:surface",
        "precip_rate": "PRATE",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [i for i in range(0, 24)],
)

NCEP_HWRF = GribDataAttributes(
    "HWRF",
    "hwrf",
    None,
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "accumulated_precip": "APCP",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [0, 6, 12, 18],
)

NCEP_WPC = GribDataAttributes(
    "WPC",
    "wpc_ncep",
    None,
    {
        "accumulated_precip": "APCP",
    },
    [0, 6, 12, 18],
)
