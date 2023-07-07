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
import tempfile
import boto3
from datetime import datetime


class CtcxDownloader:
    """
    This class is responsible for downloading the CTCX data from S3.
    """

    def __init__(self):
        """
        Initialize the downloader using the environment variables.

        Environment Variables Used:
            COAMPS_S3_BUCKET: The name of the S3 bucket to download from
            COAMPS_AWS_KEY: The AWS key to use for authentication
            COAMPS_AWS_SECRET: The AWS secret to use for authentication
        """
        import os
        from .metdb import Metdb
        from .s3file import S3file

        self.__s3_bucket = os.environ["COAMPS_S3_BUCKET"]

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
        self.__bucket = self.__resource.Bucket(self.__s3_bucket)
        self.__temp_directory = tempfile.mkdtemp()
        self.__database = Metdb()
        self.__s3 = S3file()

    def __del__(self):
        import shutil
        import logging

        log = logging.getLogger(__name__)

        log.info("Removing temporary directory")
        shutil.rmtree(self.__temp_directory)

    def download(self) -> int:
        """
        Download the CTCX data from S3.

        Returns:
            The number of files downloaded
        """
        from datetime import datetime
        import logging
        import os

        log = logging.getLogger(__name__)

        current_year = datetime.utcnow().year - 1

        STORM_MIN = 1
        STORM_MAX = 41

        file_count = 0

        for st in range(STORM_MIN, STORM_MAX, 1):
            storm_name = "{:02d}L".format(st)
            prefix = "CTCX/{:04d}/{:s}/".format(current_year, storm_name)
            objects = self.__bucket.objects.filter(Prefix=prefix)
            for obj in objects:
                path = obj.key

                if path.endswith(".tar.gz"):

                    log.info("Begin processing file {:s}".format(path))

                    cycle_date = datetime.strptime(
                        os.path.basename(path),
                        "CTCXEPS_{:s}.%Y%m%d%H.tar.gz".format(storm_name),
                    )

                    has_missing_cycles = self.__check_database_for_ensemble_members(
                        cycle_date, storm_name
                    )

                    if has_missing_cycles:
                        file_count += self.__process_ctcx_ensemble(path, storm_name)
                    else:
                        log.info("Skipping file {:s}".format(path))

        return file_count

    def __process_ctcx_ensemble(self, path: str, storm_name: str) -> int:
        """
        Process the CTCX ensemble file.

        Args:
            path: The path to the file
            storm_name: The name of the storm

        Returns:
            The number of files processed
        """
        import logging
        import os

        log = logging.getLogger(__name__)

        file_count = 0

        info = self.__retrieve_files_from_s3(path, storm_name)
        archive_filename = info["filename"]

        # ...Get the base name of the file (without the extension)
        base_name = archive_filename[: -len(".tar.gz")]
        directory = os.path.join(self.__temp_directory, base_name)

        # ...Convert the hdf5 files to netCDF format
        log.info(
            "Begin converting hdf5 files to netCDF format in directory {:s}".format(
                directory
            )
        )

        for filename in os.listdir(directory):
            if filename.endswith(".hdf5"):
                ensemble_member = self.__process_hdf5_file(base_name, filename)

                if ensemble_member:
                    self.__add_member_to_db_and_upload(
                        base_name, storm_name, ensemble_member
                    )
                    file_count += ensemble_member["n_snaps"]

        return file_count

    def __check_database_for_ensemble_members(
        self, cycle_date: datetime, storm_name: str
    ):
        """
        Check the database to see if we have all the ensemble members for a given cycle date.

        Args:
            cycle_date: The cycle date to check
            storm_name: The name of the storm

        Returns:
            True if we have all the ensemble members for the given cycle date, False otherwise

        """
        import logging

        log = logging.getLogger(__name__)

        ENSEMBLE_MEMBER_MIN = 0
        ENSEMBLE_MEMBER_MAX = 20

        has_missing_cycles = False

        for ensemble_member in range(ENSEMBLE_MEMBER_MIN, ENSEMBLE_MEMBER_MAX + 1, 1):

            # ...Scan the database quickly to see if we can skip this file
            metadata = {
                "name": storm_name,
                "ensemble_member": ensemble_member,
                "cycledate": cycle_date,
                "forecastdate": cycle_date,
            }

            if not self.__database.has("ctcx", metadata):
                log.info(
                    "Could not find ensemble member {:d} in database for cycle {:s}, storm {:s}".format(
                        ensemble_member, cycle_date.strftime("%Y%m%d%H"), storm_name
                    )
                )
                has_missing_cycles = True
                break

        return has_missing_cycles

    def __add_member_to_db_and_upload(
        self, base_name: str, storm_name: str, ensemble_member: dict
    ):
        """
        Add the ensemble member to the database and upload the file to S3.

        Args:
            base_name: The base name of the file (without the extension)
            ensemble_member: The ensemble member metadata to add
        """
        import os
        import logging
        from datetime import timedelta

        log = logging.getLogger(__name__)

        # ...Add the ensemble member to the database
        log.info(
            "Begin adding ensemble member {:s} to database".format(
                ensemble_member["member"]
            )
        )

        member_id = ensemble_member["member"]

        for snapshot in ensemble_member["info"]:
            year_str = snapshot["cycle"].strftime("%Y")
            date_str = snapshot["cycle"].strftime("%Y%m%d")
            hour_str = snapshot["cycle"].strftime("%H")
            forecast_date = snapshot["cycle"] + timedelta(hours=snapshot["tau"])

            metadata = {
                "cycledate": snapshot["cycle"],
                "forecastdate": forecast_date,
                "name": storm_name,
                "ensemble_member": int(member_id),
            }

            if self.__database.has("ctcx", metadata):
                log.debug(
                    "Skipping ensemble member {:s} for cycle {:s}, hour {:d}".format(
                        member_id,
                        snapshot["cycle"].strftime("%Y%m%d%H"),
                        snapshot["tau"],
                    )
                )
                for domain in snapshot["domains"]:
                    os.remove(domain)
            else:
                domain_files = ""
                for domain in snapshot["domains"]:
                    s3_path = os.path.join(
                        "coamps_ctcx",
                        year_str,
                        storm_name,
                        date_str,
                        hour_str,
                        member_id,
                        os.path.basename(domain),
                    )
                    domain_files += s3_path + ","
                    self.__s3.upload_file(domain, s3_path)
                    os.remove(domain)

                domain_files = domain_files[:-1]

                # ...Add to the database
                self.__database.add(
                    metadata,
                    "ctcx",
                    domain_files,
                )

    def __retrieve_files_from_s3(self, path: str, storm_name: str) -> dict:
        """
        Retrieve the files from S3 and return a dict with the metadata.

        Args:
            path: The path to the file in S3
            storm_name: The name of the storm

        Returns:
            A dict with the metadata
        """
        import os
        from datetime import datetime
        import tarfile
        import logging

        log = logging.getLogger(__name__)

        # ...Get the metadata from the filename
        filename = os.path.basename(path)
        cycle_date = datetime.strptime(
            filename, "CTCXEPS_{:s}.%Y%m%d%H.tar.gz".format(storm_name)
        )

        # ...Retrieve file from S3
        log.info("Begin downloading file {:s} from s3".format(path))
        local_file = os.path.join(self.__temp_directory, filename)
        self.__bucket.download_file(path, local_file)

        # ...Unpack the tarball
        log.info("Begin unpacking file {:s}".format(local_file))
        tar = tarfile.open(local_file)
        tar.extractall(path=self.__temp_directory)
        tar.close()

        return {
            "filename": filename,
            "cycle_date": cycle_date,
        }

    def __process_hdf5_file(self, base_name: str, filename: str) -> dict:
        """
        Process the hdf5 file and convert it to netCDF format and return a dict with the metadata.

        Args:
            base_name: The base name of the file (without the extension)
            filename: The name of the file

        Returns:
            A dict with the metadata
        """
        from .ctcxformatter import CtcxFormatter
        import logging
        import os

        log = logging.getLogger(__name__)

        ensemble_member = int(filename.split("_")[0][-3:])
        ensemble_member_str = "{:03d}".format(ensemble_member)

        member_directory = os.path.join(
            self.__temp_directory, base_name, ensemble_member_str
        )
        os.mkdir(member_directory)
        log.info(
            "Processing ensemble member {:03d} in folder {:s}".format(
                ensemble_member, member_directory
            )
        )

        formatter = CtcxFormatter(
            os.path.join(self.__temp_directory, base_name, filename),
            member_directory,
        )
        n_snaps = formatter.n_time_steps()
        file_info = formatter.write()

        return {
            "member": ensemble_member_str,
            "directory": member_directory,
            "n_snaps": n_snaps,
            "info": file_info,
        }
