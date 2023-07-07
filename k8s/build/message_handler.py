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
import logging
import os
from datetime import datetime, timedelta
from typing import Tuple

import pymetbuild
from metbuild.domain import Domain
from metbuild.filelist import Filelist
from metbuild.input import Input
from metbuild.s3file import S3file
from metbuild.tables import RequestTable
from metbuild.s3gribio import S3GribIO


class MessageHandler:
    """
    This class is used to handle the messages from the queue
    and process them into met fields
    """

    def __init__(self, message: dict) -> None:
        self.__message = message
        self.__input = Input(self.__message)

    def input(self) -> Input:
        """
        Returns the input object that was created from the message

        Returns:
            Input: The input object
        """
        return self.__input

    def process_message(self) -> bool:
        """
        Process a message from the queue of available messages

        Returns:
            True if the message was processed successfully, False otherwise
        """
        import json

        filelist_name = "filelist.json"

        log = logging.getLogger(__name__)

        log.info("Processing message")
        log.info(json.dumps(self.__message))

        log.info(
            "Found {:d} domains in input request".format(self.__input.num_domains())
        )

        start_date = self.__input.start_date()
        start_date_pmb = self.__input.start_date_pmb()
        end_date = self.__input.end_date()
        end_date_pmb = self.__input.end_date_pmb()
        time_step = self.__input.time_step()

        met_field = MessageHandler.__generate_met_field(
            self.__input.format(),
            start_date_pmb,
            end_date_pmb,
            time_step,
            self.__input.filename(),
            self.__input.compression(),
        )

        log.info("Generating type key for {:s}".format(self.__input.data_type()))
        data_type_key = MessageHandler.__generate_datatype_key(self.__input.data_type())

        domain_data = []
        ongoing_restore = False
        nhc_data = {}
        db_files = []

        # ...Take a first pass on the data and check for restore status
        for i in range(self.__input.num_domains()):
            if met_field:
                log.info("Generating met domain object for domain {:d}".format(i))
                MessageHandler.__generate_met_domain(self.__input, met_field, i)
            d = self.__input.domain(i)

            log.info("Querying database for available data")
            filelist = Filelist(
                d.service(),
                self.__input.data_type(),
                start_date,
                end_date,
                d.tau(),
                d.storm_year(),
                d.storm(),
                d.basin(),
                d.advisory(),
                self.__input.nowcast(),
                self.__input.multiple_forecasts(),
                d.ensemble_member(),
            )
            f = filelist.files()
            log.info("Selected {:d} files for interpolation".format(len(f)))

            if d.service() == "nhc":
                nhc_data[i] = f
            else:
                db_files.append(f)
                if len(f) < 2:
                    log.error("No data found for domain " + str(i) + ". Giving up.")
                    raise RuntimeError("No data found for domain")
                ongoing_restore = MessageHandler.__check_glacier_restore(d, f)

        # ...If restore ongoing, this is where we stop
        if ongoing_restore:
            log.info("Request is currently in restore status")
            RequestTable.update_request(
                self.__input.request_id(),
                "restore",
                self.__message["api_key"],
                self.__message["source_ip"],
                self.__message,
                "Job is in archive restore status",
            )
            if met_field:
                ff = met_field.filenames()
                for f in ff:
                    os.remove(f)
                MessageHandler.__cleanup_temp_files(domain_data)
            return False

        # ...Begin downloading data from s3
        MessageHandler.__download_files_from_s3(
            db_files, domain_data, self.__input, met_field, nhc_data
        )

        if not met_field:
            (
                output_file_list,
                files_used_list,
            ) = MessageHandler.__generate_raw_files_list(domain_data, self.__input)
        else:
            (
                output_file_list,
                files_used_list,
            ) = MessageHandler.__interpolate_wind_fields(
                self.__input,
                met_field,
                data_type_key,
                domain_data,
                start_date,
                end_date,
                time_step,
            )

        output_file_dict = {
            "input": self.__input.json(),
            "input_files": files_used_list,
            "output_files": output_file_list,
        }

        met_field = None  # ... This assignment closes all open files

        # ...Posts the data out to the correct S3 location
        s3up = S3file(os.environ["METGET_S3_BUCKET_UPLOAD"])
        for f in output_file_list:
            path = os.path.join(self.__input.request_id(), f)
            s3up.upload_file(f, path)
            os.remove(f)

        with open(filelist_name, "w") as of:
            of.write(json.dumps(output_file_dict, indent=2))

        filelist_path = os.path.join(self.__input.request_id(), filelist_name)
        s3up.upload_file(filelist_name, filelist_path)
        log.info("Finished processing message with id")
        os.remove(filelist_name)

        MessageHandler.__cleanup_temp_files(domain_data)

        return True

    @staticmethod
    def __date_span(start_date: datetime, end_date: datetime, delta: timedelta):
        """
        Generator function that yields a series of dates between the start and end

        Args:
            start_date: The start date
            end_date: The end date
            delta: The time step in seconds

        Returns:
            A generator object that yields a series of dates between the start and end
        """
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += delta

    @staticmethod
    def __generate_datatype_key(data_type: str) -> int:
        """
        Generate the key for the data type from the pymetbuild library

        Args:
            data_type: The data type to generate the key for

        Returns:
            The key for the data type
        """
        if data_type == "wind_pressure":
            return pymetbuild.WIND_PRESSURE
        elif data_type == "pressure":
            return pymetbuild.PRESSURE
        elif data_type == "wind":
            return pymetbuild.WIND
        elif data_type == "rain":
            return pymetbuild.RAINFALL
        elif data_type == "humidity":
            return pymetbuild.HUMIDITY
        elif data_type == "temperature":
            return pymetbuild.TEMPERATURE
        elif data_type == "ice":
            return pymetbuild.ICE
        else:
            raise RuntimeError("Invalid data type requested")

    @staticmethod
    def __generate_data_source_key(data_source: str) -> int:
        """
        Generate the key for the data source from the pymetbuild library

        Args:
            data_source: The data source to generate the key for

        Returns:
            The key for the data source
        """
        if data_source == "gfs-ncep":
            return pymetbuild.Meteorology.GFS
        elif data_source == "gefs-ncep":
            return pymetbuild.Meteorology.GEFS
        elif data_source == "nam-ncep":
            return pymetbuild.Meteorology.NAM
        elif data_source == "hwrf":
            return pymetbuild.Meteorology.HWRF
        elif data_source == "hrrr-ncep":
            return pymetbuild.Meteorology.HRRR_CONUS
        elif data_source == "hrrr-alaska-ncep":
            return pymetbuild.Meteorology.HRRR_ALASKA
        elif data_source == "wpc-ncep":
            return pymetbuild.Meteorology.WPC
        elif data_source == "coamps-tc" or data_source == "coamps-ctcx":
            return pymetbuild.Meteorology.COAMPS
        else:
            raise RuntimeError("Invalid data source")

    @staticmethod
    def __generate_met_field(
        output_format: str,
        start: datetime,
        end: datetime,
        time_step: int,
        filename: str,
        compression: bool,
    ):
        """
        Generate the met field object from the pymetbuild library

        Args:
            output_format: The output format to generate the met field object for
            start: The start date
            end: The end date
            time_step: The time step in seconds
            filename: The filename to write to
            compression: Whether to compress the output
        """

        if (
            output_format == "ascii"
            or output_format == "owi-ascii"
            or output_format == "adcirc-ascii"
        ):
            return pymetbuild.OwiAscii(start, end, time_step, compression)
        elif output_format == "owi-netcdf" or output_format == "adcirc-netcdf":
            return pymetbuild.OwiNetcdf(start, end, time_step, filename)
        elif output_format == "hec-netcdf":
            return pymetbuild.RasNetcdf(start, end, time_step, filename)
        elif output_format == "delft3d":
            return pymetbuild.DelftOutput(start, end, time_step, filename)
        elif output_format == "raw":
            return None
        else:
            raise RuntimeError(
                "Invalid output format selected: {:s}".format(output_format)
            )

    @staticmethod
    def __generate_met_domain(input_data: Input, met_object, index: int):
        """
        Generate the met domain object from the pymetbuild library

        Args:
            input_data: The input data object
            met_object: The met object
            index: The index of the domain to generate

        Returns:
            The met domain object
        """

        d = input_data.domain(index)
        output_format = input_data.format()
        if (
            output_format == "ascii"
            or output_format == "owi-ascii"
            or output_format == "adcirc-ascii"
        ):
            if input_data.data_type() == "wind_pressure":
                fn1 = input_data.filename() + "_" + "{:02d}".format(index) + ".pre"
                fn2 = input_data.filename() + "_" + "{:02d}".format(index) + ".wnd"
                fns = [fn1, fn2]
            elif input_data.data_type() == "rain":
                fns = [input_data.filename() + ".precip"]
            elif input_data.data_type() == "humidity":
                fns = [input_data.filename() + ".humid"]
            elif input_data.data_type() == "ice":
                fns = [input_data.filename() + ".ice"]
            else:
                raise RuntimeError("Invalid variable requested")
            if input_data.compression():
                for i, s in enumerate(fns):
                    fns[i] = s + ".gz"

            met_object.addDomain(d.grid().grid_object(), fns)
        elif output_format == "owi-netcdf":
            group = d.name()
            met_object.addDomain(d.grid().grid_object(), [group])
        elif output_format == "hec-netcdf":
            if input_data.data_type() == "wind_pressure":
                variables = ["wind_u", "wind_v", "mslp"]
            elif input_data.data_type() == "wind":
                variables = ["wind_u", "wind_v"]
            elif input_data.data_type() == "rain":
                variables = ["rain"]
            elif input_data.data_type() == "humidity":
                variables = ["humidity"]
            elif input_data.data_type() == "ice":
                variables = ["ice"]
            else:
                raise RuntimeError("Invalid variable requested")
            met_object.addDomain(d.grid().grid_object(), variables)
        elif output_format == "delft3d":
            if input_data.data_type() == "wind_pressure":
                variables = ["wind_u", "wind_v", "mslp"]
            elif input_data.data_type() == "wind":
                variables = ["wind_u", "wind_v"]
            elif input_data.data_type() == "rain":
                variables = ["rain"]
            elif input_data.data_type() == "humidity":
                variables = ["humidity"]
            elif input_data.data_type() == "ice":
                variables = ["ice"]
            else:
                raise RuntimeError("Invalid variable requested")
            met_object.addDomain(d.grid().grid_object(), variables)
        else:
            raise RuntimeError("Invalid output format selected: " + output_format)

    @staticmethod
    def __merge_nhc_tracks(
        besttrack_file: str, forecast_file: str, output_file: str
    ) -> str:
        """
        Merge the best track and forecast files into a single file

        Args:
            besttrack_file: The best track file
            forecast_file: The forecast file
            output_file: The output file

        Returns:
            The output file

        """

        from datetime import datetime, timedelta

        btk_lines = []
        fcst_lines = []

        with open(besttrack_file) as btk:
            for line in btk:
                btk_lines.append(
                    {
                        "line": line.rstrip(),
                        "date": datetime.strptime(line.split(",")[2], " %Y%m%d%H"),
                    }
                )

        with open(forecast_file) as fcst:
            for line in fcst:
                fcst_basetime = datetime.strptime(line.split(",")[2], " %Y%m%d%H")
                fcst_time = int(line.split(",")[5])
                fcst_lines.append(
                    {
                        "line": line.rstrip(),
                        "date": fcst_basetime + timedelta(hours=fcst_time),
                    }
                )

        start_date = btk_lines[0]["date"]
        start_date_str = datetime.strftime(start_date, "%Y%m%d%H")

        with open(output_file, "w") as merge:
            for line in btk_lines:
                if line["date"] < fcst_lines[0]["date"]:
                    dt = int((line["date"] - start_date).total_seconds() / 3600.0)
                    dt_str = "{:4d}".format(dt)
                    sub1 = line["line"][:8]
                    sub2 = line["line"][18:29]
                    sub3 = line["line"][33:]
                    line_new = sub1 + start_date_str + sub2 + dt_str + sub3
                    merge.write(line_new + "\n")

            for line in fcst_lines:
                dt = int((line["date"] - start_date).total_seconds() / 3600.0)
                dt_str = "{:4d}".format(dt)
                sub1 = line["line"][:8]
                sub2 = line["line"][18:29]
                sub3 = line["line"][33:]
                line_new = sub1 + start_date_str + sub2 + dt_str + sub3
                merge.write(line_new + "\n")

        return output_file

    @staticmethod
    def __interpolate_wind_fields(
        input_data,
        met_field,
        data_type_key,
        domain_data,
        start_date,
        end_date,
        time_step,
    ) -> Tuple[list, dict]:
        """
        Interpolates the wind fields for the given domains

        Args:
            input_data (Input): The input data
            met_field (Meteorology): The meteorology object
            data_type_key (int): The data type key
            domain_data (list): The list of domain data
            start_date (datetime): The start date
            end_date (datetime): The end date
            time_step (int): The time step

        Returns:
            Tuple[list, dict]: The list of output files and the list of files used
        """
        from datetime import timedelta

        log = logging.getLogger(__name__)

        files_used_list = {}

        for i in range(input_data.num_domains()):
            d = input_data.domain(i)

            if d.service() == "nhc":
                log.error("NHC to gridded data not implemented")
                raise RuntimeError("NHC to gridded data no implemented")

            source_key = MessageHandler.__generate_data_source_key(d.service())
            met = pymetbuild.Meteorology(
                d.grid().grid_object(),
                source_key,
                data_type_key,
                input_data.backfill(),
                input_data.epsg(),
            )

            t0 = domain_data[i][0]["time"]

            domain_files_used = []
            next_time = start_date + timedelta(seconds=time_step)
            index = MessageHandler.__get_next_file_index(next_time, domain_data[i])

            t1 = domain_data[i][index]["time"]
            ff = domain_data[i][0]["filepath"]
            MessageHandler.__print_file_status(ff, t0)

            met.set_next_file(ff)
            if d.service() == "coamps-tc" or d.service() == "coamps-ctcx":
                for ff in domain_data[i][0]["filepath"]:
                    domain_files_used.append(os.path.basename(ff))
            else:
                domain_files_used.append(
                    os.path.basename(domain_data[i][0]["filepath"])
                )

            met.set_next_file(domain_data[i][index]["filepath"])
            ff = domain_data[i][index]["filepath"]
            MessageHandler.__print_file_status(ff, t1)
            met.process_data()
            if d.service() == "coamps-tc" or d.service() == "coamps-ctcx":
                for ff in domain_data[i][index]["filepath"]:
                    domain_files_used.append(os.path.basename(ff))
            else:
                domain_files_used.append(
                    os.path.basename(domain_data[i][index]["filepath"])
                )

            for t in MessageHandler.__date_span(
                start_date, end_date, timedelta(seconds=time_step)
            ):
                if t > t1:
                    index = MessageHandler.__get_next_file_index(t, domain_data[i])
                    t0 = t1
                    t1 = domain_data[i][index]["time"]
                    ff = domain_data[i][index]["filepath"]
                    MessageHandler.__print_file_status(ff, t1)
                    met.set_next_file(domain_data[i][index]["filepath"])
                    if t0 != t1:
                        if d.service() == "coamps-tc" or d.service() == "coamps-ctcx":
                            for ff in domain_data[i][index]["filepath"]:
                                domain_files_used.append(os.path.basename(ff))
                        else:
                            domain_files_used.append(
                                os.path.basename(domain_data[i][index]["filepath"])
                            )
                    met.process_data()

                if t < t0 or t > t1:
                    weight = -1.0
                elif t0 == t1:
                    weight = 0.0
                else:
                    weight = met.generate_time_weight(
                        Input.date_to_pmb(t0),
                        Input.date_to_pmb(t1),
                        Input.date_to_pmb(t),
                    )

                log.info(
                    "Processing time {:s}, weight = {:f}".format(
                        t.strftime("%Y-%m-%d %H:%M"), weight
                    )
                )

                log.info(
                    "Interpolating domain {:d}, snap {:s} to grid".format(
                        i, t.strftime("%Y-%m-%d %H:%M")
                    )
                )
                if input_data.data_type() == "wind_pressure":
                    values = met.to_wind_grid(weight)
                else:
                    values = met.to_grid(weight)

                log.info(
                    "Writing domain {:d}, snap {:s} to disk".format(
                        i, t.strftime("%Y-%m-%d %H:%M")
                    )
                )
                met_field.write(Input.date_to_pmb(t), i, values)

            files_used_list[input_data.domain(i).name()] = domain_files_used

        output_file_list = met_field.filenames()

        return output_file_list, files_used_list

    @staticmethod
    def __generate_raw_files_list(domain_data, input_data) -> Tuple[list, dict]:
        """
        Generates the list of raw files used for the given domains

        Args:
            domain_data (list): The list of domain data
            input_data (Input): The input data

        Returns:
            Tuple[list, dict]: The list of raw files and the list of files used
        """
        output_file_list = []
        files_used_list = {}
        for i in range(input_data.num_domains()):
            for pr in domain_data[i]:
                output_file_list.append(pr["filepath"])
            files_used_list[input_data.domain(i).name()] = output_file_list
        return output_file_list, files_used_list

    @staticmethod
    def __download_files_from_s3(
        db_files, domain_data, input_data, met_field, nhc_data
    ) -> None:
        """
        Downloads the files from S3 and generates the list of files used

        Args:
            db_files (list): The list of files from the database
            domain_data (list): The list of domain data
            input_data (Input): The input data
            met_field (MeteorologyField): The meteorology field
            nhc_data (dict): The list of NHC data

        Returns:
            None
        """
        for i in range(input_data.num_domains()):
            d = input_data.domain(i)
            domain_data.append([])

            if d.service() == "nhc":
                MessageHandler.__generate_merged_nhc_files(
                    d, domain_data, i, met_field, nhc_data
                )
            else:
                MessageHandler.__get_2d_forcing_files(
                    input_data.data_type(), d, db_files, domain_data, i, met_field
                )

    @staticmethod
    def __generate_noaa_s3_remote_instance(data_type: str) -> S3GribIO:
        """
        Generates the remote s3 grib instance for NOAA S3 archived files

        Args:
            data_type (str): The data type

        Returns:
            S3GribIO: The remote s3 grib instance
        """
        from metbuild.gribdataattributes import (
            NCEP_NAM,
            NCEP_GFS,
            NCEP_GEFS,
            NCEP_HRRR,
            NCEP_HRRR_ALASKA,
            NCEP_WPC,
        )

        remote = None

        if data_type == "gfs-ncep":
            grib_attrs = NCEP_GFS
        elif data_type == "nam-ncep":
            grib_attrs = NCEP_NAM
        elif data_type == "gefs-ncep":
            grib_attrs = NCEP_GEFS
        elif data_type == "hrrr-ncep":
            grib_attrs = NCEP_HRRR
        elif data_type == "hrrr-alaska-ncep":
            grib_attrs = NCEP_HRRR_ALASKA
        elif data_type == "wpc-ncep":
            grib_attrs = NCEP_WPC
        else:
            grib_attrs = None

        if grib_attrs is not None:
            remote = S3GribIO(grib_attrs.bucket(), grib_attrs.variables())

        return remote

    @staticmethod
    def __get_2d_forcing_files(
        data_type: str,
        domain: Domain,
        db_files: list,
        domain_data: list,
        index: int,
        met_field,
    ) -> None:
        """
        Gets the 2D forcing files from s3

        Args:
            data_type (str): The data type
            domain (Domain): The domain
            db_files (list): The list of files from the database
            domain_data (list): The list of domain data
            index (int): The index of the domain
            met_field (MeteorologyField): The meteorology field

        Returns:
            None

        """
        import tempfile

        log = logging.getLogger(__name__)

        s3 = S3file(os.environ["METGET_S3_BUCKET"])
        s3_remote = MessageHandler.__generate_noaa_s3_remote_instance(domain.service())

        f = db_files[index]
        if len(f) < 2:
            log.error("No data found for domain {:d}. Giving up.".format(index))
            raise RuntimeError(
                "No data found for domain {:d}. Giving up.".format(index)
            )
        for item in f:
            if domain.service() == "coamps-tc" or domain.service() == "coamps-ctcx":
                files = item["filepath"].split(",")
                local_file_list = []
                for ff in files:
                    local_file = s3.download(ff, domain.service(), item["forecasttime"])
                    if not met_field:
                        new_file = os.path.basename(local_file)
                        os.rename(local_file, new_file)
                        local_file = new_file
                    local_file_list.append(local_file)
                domain_data[index].append(
                    {"time": item["forecasttime"], "filepath": local_file_list}
                )
            else:
                if "s3://" in item["filepath"]:
                    tempdir = tempfile.gettempdir()
                    fn = os.path.split(item["filepath"])[1]
                    fname = "{:s}.{:s}.{:s}".format(
                        domain.service(),
                        item["forecasttime"].strftime("%Y%m%d%H%M"),
                        fn,
                    )
                    local_file = os.path.join(tempdir, fname)
                    success, fatal = s3_remote.download(
                        item["filepath"], local_file, data_type
                    )
                    if not success and fatal:
                        raise RuntimeError(
                            "Unable to download file {:s}".format(item["filepath"])
                        )
                else:
                    local_file = s3.download(
                        item["filepath"], domain.service(), item["forecasttime"]
                    )
                    success = True
                if not met_field:
                    new_file = os.path.basename(local_file)
                    os.rename(local_file, new_file)
                    local_file = new_file

                if success:
                    domain_data[index].append(
                        {"time": item["forecasttime"], "filepath": local_file}
                    )

    @staticmethod
    def __print_file_status(filepath: any, time: datetime) -> None:
        """
        Print the status of the file being processed to the screen

        Args:
            filepath: The file being processed
            time: The time of the file being processed
        """

        log = logging.getLogger(__name__)

        if type(filepath) == list:
            fnames = ""
            for fff in filepath:
                if fnames == "":
                    fnames += os.path.basename(fff)
                else:
                    fnames += ", " + os.path.basename(fff)
        else:
            fnames = filepath
        log.info(
            "Processing next file: {:s} ({:s})".format(
                fnames, time.strftime("%Y-%m-%d %H:%M")
            )
        )

    @staticmethod
    def __get_next_file_index(time: datetime, domain_data):
        """
        Get the index of the next file to process in the domain data list

        Args:
            time: The time of the file being processed
            domain_data: The list of files to process
        """
        for ii in range(len(domain_data)):
            if time <= domain_data[ii]["time"]:
                return ii
        return len(domain_data) - 1

    @staticmethod
    def __generate_merged_nhc_files(
        domain, domain_data, index, met_field, nhc_data
    ) -> None:
        """
        Generates the merged NHC files for the given domain which are returned

        Args:
            domain (Domain): The domain
            domain_data (list): The list of domain data
            index (int): The index of the domain
            met_field (MeteorologyField): The meteorology field
            nhc_data (dict): The list of NHC data

        Returns:
            None
        """

        log = logging.getLogger(__name__)

        s3 = S3file(os.environ["METGET_S3_BUCKET"])

        if not nhc_data[index]["best_track"] and not nhc_data[index]["forecast_track"]:
            log.error("No data found for domain {:d}. Giving up".format(index))
            raise RuntimeError("No data found for domain {:d}. Giving up".format(index))
        local_file_besttrack = None
        local_file_forecast = None
        if nhc_data[index]["best_track"]:
            local_file_besttrack = s3.download(
                nhc_data[index]["best_track"]["filepath"], "nhc"
            )
            if not met_field:
                new_file = os.path.basename(local_file_besttrack)
                os.rename(local_file_besttrack, new_file)
                local_file_besttrack = new_file
            domain_data[index].append(
                {
                    "time": nhc_data[index]["best_track"]["start"],
                    "filepath": local_file_besttrack,
                }
            )
        if nhc_data[index]["forecast_track"]:
            local_file_forecast = s3.download(
                nhc_data[index]["forecast_track"]["filepath"], "nhc"
            )
            if not met_field:
                new_file = os.path.basename(local_file_forecast)
                os.rename(local_file_forecast, new_file)
                local_file_forecast = new_file
            domain_data[index].append(
                {
                    "time": nhc_data[index]["forecast_track"]["start"],
                    "filepath": local_file_forecast,
                }
            )
        if nhc_data[index]["best_track"] and nhc_data[index]["forecast_track"]:
            merge_file = "nhc_merge_{:04d}_{:s}_{:s}_{:s}.trk".format(
                nhc_data[index]["best_track"]["start"].year,
                domain.basin(),
                domain.storm(),
                domain.advisory(),
            )
            local_file_merged = MessageHandler.__merge_nhc_tracks(
                local_file_besttrack, local_file_forecast, merge_file
            )
            domain_data[index].append(
                {
                    "time": nhc_data[index]["best_track"]["start"],
                    "filepath": local_file_merged,
                }
            )

    @staticmethod
    def __check_glacier_restore(domain: Domain, filelist: list) -> bool:
        """
        Checks the list of files to see if any are currently being restored from Glacier

        Args:
            domain (Domain): Domain object
            filelist (list): List of dictionaries containing the filepaths of the
                files to be processed

        Returns:
            bool: True if any files are currently being restored from Glacier

        """
        s3 = S3file(os.environ["METGET_S3_BUCKET"])
        ongoing_restore = False
        for item in filelist:
            if domain.service() == "coamps-tc" or domain.service() == "coamps-ctcx":
                files = item["filepath"].split(",")
                for ff in files:
                    ongoing_restore_this = s3.check_archive_initiate_restore(ff)
                    if ongoing_restore_this:
                        ongoing_restore = True
            else:
                if "s3://" not in item["filepath"]:
                    ongoing_restore_this = s3.check_archive_initiate_restore(
                        item["filepath"]
                    )
                    if ongoing_restore_this:
                        ongoing_restore = True
        return ongoing_restore

    @staticmethod
    def __cleanup_temp_files(data: list):
        """
        Removes all temporary files created during processing

        Args:
            data (list): List of dictionaries containing the filepaths of the
        """
        from os.path import exists

        for domain in data:
            for f in domain:
                if type(f["filepath"]) == list:
                    for ff in f["filepath"]:
                        if exists(ff):
                            os.remove(ff)
                else:
                    if exists(f["filepath"]):
                        os.remove(f["filepath"])
