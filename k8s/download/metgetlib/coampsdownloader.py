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

from datetime import datetime, timedelta
from typing import Tuple


class CoampsDownloader:
    """
    Download the latest COAMPS files from the S3 bucket
    """

    STORM_MIN = 1
    STORM_MAX = 41

    def __init__(self):
        """
        Initialize the downloader
        """
        import os

        from .metdb import Metdb
        from .s3file import S3file
        import boto3
        import tempfile

        self.__s3_download_bucket = os.environ["COAMPS_S3_BUCKET"]
        self.__s3_download_prefix = "deterministic/realtime"

        if "COAMPS_AWS_KEY" in os.environ:
            self.__aws_key_id = os.environ["COAMPS_AWS_KEY"]
        else:
            self.__aws_key_id = None

        if "COAMPS_AWS_SECRET" in os.environ:
            self.__aws_access_key = os.environ["COAMPS_AWS_SECRET"]
        else:
            self.__aws_access_key = None

        if self.__aws_key_id is None or self.__aws_access_key is None:
            self.__resource = boto3.resource("s3")
        else:
            self.__resource = boto3.resource(
                "s3",
                aws_access_key_id=self.__aws_key_id,
                aws_secret_access_key=self.__aws_access_key,
            )

        self.__bucket = self.__resource.Bucket(self.__s3_download_bucket)
        self.__temp_directory = tempfile.mkdtemp(prefix="coamps_")
        self.__database = Metdb()
        self.__s3 = S3file()

    def __reset_temp_directory(self, create_new: bool) -> None:
        """
        Delete the temporary directory and create a new one if requested.
        The new directory will be saved in the __temp_directory variable.

        Args:
            create_new: Create a new temporary directory

        Returns:
            None
        """
        import shutil
        import tempfile
        import logging

        log = logging.getLogger(__name__)

        log.info("Deleting temporary directory: {}".format(self.__temp_directory))

        shutil.rmtree(self.__temp_directory)

        if create_new:
            self.__temp_directory = tempfile.mkdtemp(prefix="coamps_")
        else:
            self.__temp_directory = None

    def __del__(self):
        """
        Delete the temporary directory when the object is deleted
        """
        self.__reset_temp_directory(False)

    @staticmethod
    def __date_from_filename(filename) -> Tuple[datetime, datetime]:
        """
        Get the cycle and forecast date from the filename

        Args:
            filename: Filename to parse

        Returns:
            Tuple of cycle and forecast date
        """
        forecast_nhour = int(filename[-6:-3])
        date_str = filename[-20:-10]
        cycle_hour = datetime.strptime(date_str, "%Y%m%d%H")
        forecast_hour = cycle_hour + timedelta(hours=forecast_nhour)
        return cycle_hour, forecast_hour

    def download(self) -> int:
        """
        Download the latest COAMPS files from the S3 bucket

        Returns:
            Number of files downloaded
        """
        import logging
        import os

        log = logging.getLogger(__name__)

        current_year = datetime.utcnow().year

        file_count = 0

        for storm in range(CoampsDownloader.STORM_MIN, CoampsDownloader.STORM_MAX, 1):
            storm_name = "{:02d}L".format(storm)
            prefix = os.path.join(
                self.__s3_download_prefix, "{:04d}".format(current_year), storm_name
            )

            # ...Check if the prefix exists in s3
            forecast_list = list(self.__bucket.objects.filter(Prefix=prefix))
            if len(forecast_list) == 0:
                continue

            for forecast in forecast_list:
                filename = forecast.key.split("/")[-1]
                if "merged" in filename:
                    continue
                if "tar" not in filename:
                    continue

                date_str = filename.split("_")[1]
                cycle_date = datetime.strptime(date_str, "%Y%m%d%H")

                # ...Check if the file exists in the database
                has_all_forecast_snaps = self.__check_database_for_forecast(
                    storm_name, cycle_date
                )

                if has_all_forecast_snaps:
                    log.debug(
                        "Skipping {:s} since all forecast data exists in database".format(
                            filename
                        )
                    )
                    continue

                # ...Download the file
                files = self.__download_and_unpack_forecast(filename, forecast)
                file_list = self.__generate_forecast_snap_list(files)

                for key in file_list.keys():
                    dd = file_list[key]
                    files = ""
                    metadata = {
                        "cycledate": file_list[key][0]["cycle"],
                        "forecastdate": key,
                        "name": storm_name,
                    }
                    if self.__database.has("coamps", metadata):
                        continue

                    log.info(
                        "Adding Storm: {:s}, Cycle: {:s}, Forecast: {:s} to database".format(
                            storm_name,
                            datetime.strftime(
                                file_list[key][0]["cycle"], "%Y-%m-%d %H:%M"
                            ),
                            datetime.strftime(key, "%Y-%m-%d %H:%M"),
                        )
                    )
                    for f in dd:
                        local_file = f["filename"]
                        cycle = f["cycle"]
                        remote_path = os.path.join(
                            "coamps_tc",
                            storm_name,
                            datetime.strftime(cycle, "%Y%m%d"),
                            datetime.strftime(cycle, "%H"),
                            os.path.basename(f["filename"]),
                        )
                        self.__s3.upload_file(local_file, remote_path)
                        if files == "":
                            files += remote_path
                        else:
                            files += "," + remote_path
                    self.__database.add(metadata, "coamps", files)
                    file_count += 1

                self.__reset_temp_directory(True)

        return file_count

    @staticmethod
    def __generate_forecast_snap_list(files) -> dict:
        """
        Generate a list of forecast snapshots from the list of files

        Args:
            files: List of files to parse

        Returns:
            Dictionary of forecast snapshots
        """

        import os

        file_list = {}
        for f in files:
            cycle_date, forecast_hour = CoampsDownloader.__date_from_filename(f)
            fn = os.path.basename(f)
            domain = int(fn.split("_")[1][1:])
            if forecast_hour not in file_list.keys():
                file_list[forecast_hour] = []

            file_list[forecast_hour].append(
                {"cycle": cycle_date, "domain": domain, "filename": f}
            )

        return file_list

    def __download_and_unpack_forecast(self, filename, forecast):
        """
        Download and unpack the forecast file from the tar archive

        Args:
            filename: Filename to download
            forecast: Forecast object from S3

        Returns:
            List of netcdf files in the temporary directory
        """
        import logging
        import os
        import glob
        import tarfile

        log = logging.getLogger(__name__)

        # ...Download the file
        log.info("Downloading file: {}".format(filename))
        local_file = os.path.join(self.__temp_directory, filename)
        self.__bucket.download_file(forecast.key, local_file)

        # ...Unpack the file
        log.info("Unpacking file: {}".format(filename))
        with tarfile.open(local_file, "r") as tar:

            def is_within_directory(directory, target):

                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)

                prefix = os.path.commonprefix([abs_directory, abs_target])

                return prefix == abs_directory

            def safe_extract(
                tar_obj, extract_path=".", members=None, *, numeric_owner=False
            ):

                for member in tar_obj.getmembers():
                    member_path = os.path.join(extract_path, member.name)
                    if not is_within_directory(extract_path, member_path):
                        raise Exception("Attempted Path Traversal in tar File")

                tar_obj.extractall(extract_path, members, numeric_owner=numeric_owner)

            safe_extract(tar, self.__temp_directory)

        # ...Get the list of netcdf files in the temporary directory
        path = "{}/netcdf/*.nc".format(self.__temp_directory)
        files = sorted(glob.glob(path, recursive=True))
        return files

    def __check_database_for_forecast(
        self, storm_name: str, cycle_date: datetime
    ) -> bool:
        """
        Check if the database has all the forecast snapshots for the given storm and cycle date

        Args:
            storm_name: Name of the storm
            cycle_date: Cycle date

        Returns:
            True if all forecast snapshots exist in the database, False otherwise
        """
        has_all_forecast_snaps = True

        for tau in range(0, 126 + 1, 1):
            forecast_date = cycle_date + timedelta(hours=tau)
            metadata = {
                "name": storm_name,
                "cycledate": cycle_date,
                "forecastdate": forecast_date,
            }

            if not self.__database.has("coamps", metadata):
                has_all_forecast_snaps = False
                break

        return has_all_forecast_snaps
