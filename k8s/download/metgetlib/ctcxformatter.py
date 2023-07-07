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
import h5py
from datetime import datetime
import numpy as np
import logging


class CtcxDomain:
    """
    Class to hold the data for a single domain of a CTCX snapshot.
    """

    def __init__(
        self,
        cycle_time: datetime,
        forecast_time: datetime,
        lon: dict,
        lat: dict,
        pressure: dict,
        uwind: dict,
        vwind: dict,
    ):
        """
        Create a new CtcxDomain object.

        Args:
            cycle_time: The cycle time of the snapshot.
            forecast_time: The forecast time of the snapshot.
            lon: The longitude metadata.
            lat: The latitude metadata.
            pressure: The pressure metadata.
            uwind: The u-wind metadata.
            vwind: The v-wind metadata.
        """
        self.__cycle_time = cycle_time
        self.__forecast_time = forecast_time
        self.__lon = lon
        self.__lat = lat
        self.__pressure = pressure
        self.__uwind = uwind
        self.__vwind = vwind
        self.__filename = lon["filename"]
        self.__fid = h5py.File(self.__filename, "r")

    def __del__(self):
        """
        Close the HDF5 file.
        """
        self.__fid.close()

    def cycle_time(self) -> datetime:
        """
        Return the cycle time of the snapshot.
        """
        return self.__cycle_time

    def forecast_time(self) -> datetime:
        """
        Return the forecast time of the snapshot.
        """
        return self.__forecast_time

    def tau(self) -> int:
        """
        Return the forecast time of the snapshot in hours.
        """
        return int((self.__forecast_time - self.__cycle_time).total_seconds() / 3600.0)

    def get(self, metadata: dict) -> np.ndarray:
        """
        Return the data for the given metadata in a 2D array

        Args:
            metadata: The metadata for the variable to return.
        """
        if metadata["raw_name"] not in self.__fid.keys():
            raise Exception(
                "Variable {:s} not found in file {:s}".format(
                    metadata["name"], self.__filename
                )
            )
        return np.reshape(
            self.__fid[metadata["raw_name"]][:], (metadata["ny"], metadata["nx"])
        )

    def lon(self) -> dict:
        """
        Return the longitude metadata
        """
        return self.__lon

    def lat(self) -> dict:
        """
        Return the latitude metadata
        """
        return self.__lat

    def pressure(self) -> dict:
        """
        Return the pressure metadata
        """
        return self.__pressure

    def uwind(self) -> dict:
        """
        Return the u-wind metadata
        """
        return self.__uwind

    def vwind(self) -> dict:
        """
        Return the v-wind metadata
        """
        return self.__vwind


class CtcxSnapshot:
    """
    Class to hold the data for a single CTCX snapshot
    """

    def __init__(self, domain0: CtcxDomain, domain1: CtcxDomain, domain2: CtcxDomain):
        """
        Create a new CtcxSnapshot object.

        Args:
            domain0: The domain 0 data.
            domain1: The domain 1 data.
            domain2: The domain 2 data.
        """
        self.__domains = [domain0, domain1, domain2]

    def domain(self, domain_id: int) -> CtcxDomain:
        """
        Return the data for the given domain.

        Args:
            domain_id: The domain ID to return.

        Returns:
            The data for the given domain.
        """
        return self.__domains[domain_id]

    def cycle_time(self) -> datetime:
        """
        Return the cycle time of the snapshot.
        """
        return self.__domains[0].cycle_time()

    def forecast_time(self) -> datetime:
        """
        Return the forecast time of the snapshot.
        """
        return self.__domains[0].forecast_time()

    def write(self, prefix: str, output_directory: str) -> dict:
        """
        Write the snapshot to a set of NetCDF files (one per domain)

        Args:
            prefix: The prefix to use for the output files.
            output_directory: The directory to write the output files to.

        Returns:
            A dictionary containing the files written.

        """
        import os

        coldstart_str = self.cycle_time().strftime("%Y%m%d%H")
        tau_str = "{:03d}".format(self.domain(0).tau())

        file_format_string = "{:s}_d{:02d}_{:s}_tau{:s}.nc"

        files_written = {
            "tau": self.domain(0).tau(),
            "cycle": self.cycle_time(),
            "domains": [],
        }

        for i in range(3):
            filename = file_format_string.format(prefix, i + 1, coldstart_str, tau_str)
            output_file = os.path.join(output_directory, filename)
            self.__write_domain(output_file, self.domain(i))
            files_written["domains"].append(output_file)

        return files_written

    def __write_domain(self, filename: str, domain: CtcxDomain) -> None:
        """
        Write the given domain to a NetCDF file
        """
        from netCDF4 import Dataset

        ds = Dataset(filename, "w", format="NETCDF4")
        ds.createDimension("lon", domain.pressure()["nx"])
        ds.createDimension("lat", domain.pressure()["ny"])
        ds.createDimension("time", 1)

        time = ds.createVariable(
            "time",
            "f8",
            ("time",),
            compression="zlib",
            complevel=2,
        )
        time.standard_name = "time"
        time.units = "hours since 1970-01-01 00:00:00"
        time.calendar = "standard"
        time.axis = "T"

        lon = ds.createVariable(
            "lon",
            "f8",
            ("lat", "lon"),
            compression="zlib",
            complevel=2,
        )
        lon.standard_name = "longitude"
        lon.long_name = "longitude"
        lon.units = "degrees_east"
        lon.axis = "X"

        lat = ds.createVariable(
            "lat",
            "f8",
            ("lat", "lon"),
            compression="zlib",
            complevel=2,
        )
        lat.standard_name = "latitude"
        lat.long_name = "latitude"
        lat.units = "degrees_north"
        lat.axis = "Y"

        slpres = ds.createVariable(
            "slpres",
            "f8",
            ("lat", "lon"),
            compression="zlib",
            complevel=2,
        )
        slpres.standard_name = "sea level pressure (mb)"
        slpres.fill_value = -9999.0
        slpres.missing_value = -9999.0

        uuwind = ds.createVariable(
            "uuwind",
            "f8",
            ("lat", "lon"),
            compression="zlib",
            complevel=2,
        )
        uuwind.standard_name = "u wind at 10m (m/s)"
        uuwind.fill_value = -9999.0
        uuwind.missing_value = -9999.0

        vvwind = ds.createVariable(
            "vvwind",
            "f8",
            ("lat", "lon"),
            compression="zlib",
            complevel=2,
        )
        vvwind.standard_name = "v wind at 10m (m/s)"
        vvwind.fill_value = -9999.0
        vvwind.missing_value = -9999.0

        ds.Description = "Created by Zach Cobell, The Water Institute"
        ds.Source = "COAMPS-CTCX Ensemble HDF data"
        ds.Created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ds.variables["time"][:] = domain.forecast_time().timestamp() / 3600.0

        # ...Generate the meshgrid
        lon, lat = np.meshgrid(
            domain.get(domain.lon())[0], domain.get(domain.lat())[:, 0]
        )

        ds.variables["lon"][:] = lon
        ds.variables["lat"][:] = lat
        ds.variables["slpres"][:] = domain.get(domain.pressure())
        ds.variables["uuwind"][:] = domain.get(domain.uwind())
        ds.variables["vvwind"][:] = domain.get(domain.vwind())

        ds.close()


class CtcxFormatter:
    """
    A class for formatting CTCX data into netCDF data as expected by the MetGet system
    """

    def __init__(self, filename: str, output_directory: str):
        """
        Initialize the formatter with the given filename.

        Args:
            filename: The filename to format.
            output_directory: The directory to write the formatted data to.
        """
        self.__filename = filename
        self.__output_directory = output_directory
        self.__n_time_steps = None
        self.__snapshots = None
        self.__initialize_file()

    def n_time_steps(self) -> int:
        """
        Return the number of time steps in the file.
        """
        return self.__n_time_steps

    @staticmethod
    def parse_ctcx_variable(raw_variable_name: str, filename: str) -> dict:
        """
        Parse a CTCX variable name into a dictionary of metadata.

        Since there are no attributes in the hdf5, the variable name is used to
        get the metadata.
        """
        from datetime import timedelta

        variable_split = raw_variable_name.split("_")

        variable_name = variable_split[0]
        variable_level = variable_split[1]
        domain_id = int(variable_split[4][0])
        domain_nx = int(variable_split[4][2:6])
        domain_ny = int(variable_split[4][7:11])
        forecast_cycle = datetime.strptime(variable_split[5], "%Y%m%d%H")
        forecast_hour = int(variable_split[6][0:4])
        forecast_minute = int(variable_split[6][4:6])
        forecast_time = forecast_cycle + timedelta(
            hours=forecast_hour, minutes=forecast_minute
        )

        return {
            "filename": filename,
            "raw_name": raw_variable_name,
            "name": variable_name,
            "level": variable_level,
            "domain": domain_id,
            "nx": domain_nx,
            "ny": domain_ny,
            "cycle_time": forecast_cycle,
            "forecast_time": forecast_time,
            "tau": forecast_hour,
        }

    def __initialize_file(self) -> None:
        """
        Initialize the file by reading the metadata.
        """

        log = logging.getLogger(__name__)

        longitude = [{}, {}, {}]
        latitude = [{}, {}, {}]
        pressure = [{}, {}, {}]
        uwind = [{}, {}, {}]
        vwind = [{}, {}, {}]

        with h5py.File(self.__filename, "r") as f:
            for i, variable_name in enumerate(f.keys()):
                metadata = CtcxFormatter.parse_ctcx_variable(
                    variable_name, self.__filename
                )
                if metadata["name"] == "longit":
                    longitude[metadata["domain"] - 1][metadata["tau"]] = metadata
                elif metadata["name"] == "latitu":
                    latitude[metadata["domain"] - 1][metadata["tau"]] = metadata
                elif metadata["name"] == "uuwind":
                    uwind[metadata["domain"] - 1][metadata["tau"]] = metadata
                elif metadata["name"] == "vvwind":
                    vwind[metadata["domain"] - 1][metadata["tau"]] = metadata
                elif metadata["name"] == "slpres":
                    pressure[metadata["domain"] - 1][metadata["tau"]] = metadata

        self.__n_time_steps = len(list(pressure[0].keys()))
        log.debug("Found {:d} time steps".format(self.__n_time_steps))

        assert len(list(pressure[0].keys())) == len(list(uwind[0].keys()))
        assert len(list(pressure[0].keys())) == len(list(vwind[0].keys()))

        self.__snapshots = []
        for i in range(self.__n_time_steps):
            d = []
            for j in range(3):
                cycle = pressure[j][i]["cycle_time"]
                forecast = pressure[j][i]["forecast_time"]
                lon = longitude[j][i]
                lat = latitude[j][i]
                p = pressure[j][i]
                u = uwind[j][i]
                v = vwind[j][i]
                d.append(CtcxDomain(cycle, forecast, lon, lat, p, u, v))

            assert len(d) == 3
            self.__snapshots.append(CtcxSnapshot(d[0], d[1], d[2]))

        assert len(self.__snapshots) == self.__n_time_steps

    def write(self, prefix: str = "ctcx") -> list:
        """
        Write the data to netCDF files

        Args:
            prefix: The prefix to use for the output files.

        Returns:
            A list of the files written.
        """
        files_written = []
        for i in range(self.__n_time_steps):
            files_written.append(
                self.__snapshots[i].write(prefix, self.__output_directory)
            )

        return files_written
