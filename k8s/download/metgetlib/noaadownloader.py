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

import boto3
from .s3file import S3file
from .metdb import Metdb
from datetime import datetime, timedelta
from typing import Tuple, Union, List


class NoaaDownloader:
    """
    Parent class for downloading noaa grib format data
    """

    def __init__(
        self,
        mettype,
        metstring,
        address,
        begin,
        end,
        use_aws_big_data=False,
        do_archive=True,
    ):
        """
        Constructor for the NoaaDownloader class. Initializes the class variables

            Args:
                mettype (str): Type of metetrology that is to be downloaded
                address (str): Server address
                begin (datetime): start date for downloaded
                end (datetime): end date for downloading
                use_aws_big_data (bool): Use AWS S3 for downloading big data'
                do_archive (bool): Archive the downloaded data. True indicates that the data will be archived in the s3 bucket. False indicates it will be left on the remote server
        """

        self.__mettype = mettype
        self.__metstring = metstring
        self.__address = address
        self.__beginDate = begin
        self.__endDate = end
        self.__database = Metdb()
        self.__use_aws_big_data = use_aws_big_data
        self.__big_data_bucket = None
        self.__cycles = None
        self.__variables = []
        self.__do_archive = do_archive

        if self.__do_archive:
            self.__s3file = S3file()
        else:
            self.__s3file = None

    def do_archive(self):
        """
        Returns whether to archive the downloaded data

        Returns:
            bool: True if the data is to be archived, else False
        """
        return self.__do_archive

    def s3file(self) -> S3file:
        """
        Returns the S3file object

        Returns:
            S3file: S3file object
        """
        return self.__s3file

    def set_cycles(self, cycle_list: list) -> None:
        """
        Sets the cycles to download

        Args:
            cycle_list (list): List of cycles to download

        Returns:
            None
        """
        self.__cycles = cycle_list

    def cycles(self) -> list:
        """
        Returns the cycles to download

        Returns:
            list: List of cycles to download
        """
        return self.__cycles

    def set_big_data_bucket(self, bucket_name: str) -> None:
        """
        Sets the bucket name for the AWS big data service
        """
        self.__big_data_bucket = bucket_name

    def big_data_bucket(self) -> str:
        """
        Returns the bucket name for the AWS big data service
        """
        return self.__big_data_bucket

    def use_big_data(self) -> bool:
        """
        Returns whether to use the AWS big data service

        Returns:
            bool: True if using AWS big data service, False otherwise
        """
        return self.__use_aws_big_data

    def add_download_variable(self, long_name: str, name: str) -> None:
        """
        Adds a variable to the list of variables to download

        Args:
            long_name (str): The long name of the variable
            name (str): The name of the variable

        Returns:
            None
        """
        self.__variables.append({"long_name": long_name, "name": name})

    def variables(self) -> List[dict]:
        """
        Returns the list of variables to download

        Returns:
            list: List of variables to download
        """
        return self.__variables

    def mettype(self) -> str:
        """
        Returns the met type

        Returns:
            str: The met type
        """
        return self.__mettype

    def metstring(self) -> str:
        """
        Returns the met string

        Returns:
            str: The met string
        """
        return self.__metstring

    def address(self) -> str:
        """
        Returns the noaa server address

        Returns:
            str: The server address
        """
        return self.__address

    def database(self) -> Metdb:
        """
        Returns the Metdb object

        Returns:
            Metdb: The Metdb object
        """
        return self.__database

    def begindate(self) -> datetime:
        """
        Returns the begin date

        Returns:
            datetime: The begin date
        """
        return self.__beginDate

    def enddate(self) -> datetime:
        """
        Returns the end date

        Returns:
            datetime: The end date
        """
        return self.__endDate

    def setbegindate(self, date: datetime) -> None:
        """
        Sets the begin date

        Args:
            date (datetime): The begin date

        Returns:
            None
        """
        self.__beginDate = date

    def setenddate(self, date: datetime) -> None:
        """
        Sets the end date

        Args:
            date (datetime): The end date

        Returns:
            None
        """
        self.__endDate = date

    def getgrib(self, info: dict, client=None) -> Tuple[str, int, int]:
        """
        Gets the grib file from the noaa server

        Args:
            info (dict): The info dictionary
            client (boto3.client): The boto3 client for AWS S3

        Returns:
            str: The path to the grib file
        """
        if self.use_big_data():
            if client is None:
                raise RuntimeError(
                    "Need client for getgrib when using AWS big data service"
                )
            return self.__get_grib_big_data(info, client)
        else:
            return self.__get_grib_noaa_servers(info)

    @staticmethod
    def __get_inventory_byte_list(
        inventory_data: list, variable: dict
    ) -> Union[dict, None]:
        """
        Gets the byte list for the variable from the inventory data

        Args:
            inventory_data (list): The inventory data
            variable (dict): The variable dictionary

        Returns:
            dict: The byte list for the variable
        """
        for i in range(len(inventory_data)):
            if variable["long_name"] in inventory_data[i]:
                start_bits = inventory_data[i].split(":")[1]
                if i + 1 == len(inventory_data):
                    end_bits = ""
                else:
                    end_bits = inventory_data[i + 1].split(":")[1]
                return {"name": variable["name"], "start": start_bits, "end": end_bits}
        return None

    @staticmethod
    def __try_get_object(
        bucket: str, key: str, s3_client: boto3.client, byte_range: str = None
    ) -> dict:
        """
        Try to get an object from an s3 bucket. If the object does not exist, wait 5 seconds and try again.

        Args:
            bucket (str): The name of the bucket
            key (str): The key of the object
            s3_client (boto3.client): The s3 client to use
            byte_range (str): The byte range to get

        Returns:
            The object from the bucket
        """
        from botocore.exceptions import ClientError
        from time import sleep

        max_tries = 5
        sleep_interval = 5
        tries = 0

        while True:
            try:
                if byte_range:
                    return s3_client.get_object(
                        Bucket=bucket, Key=key, Range=byte_range
                    )
                else:
                    return s3_client.get_object(Bucket=bucket, Key=key)
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    tries += 1
                    sleep(sleep_interval)
                    if tries > max_tries:
                        raise RuntimeError(
                            "Could not find key {} in bucket {}".format(key, bucket)
                        )
                else:
                    raise e

    def __get_inventory_big_data(self, info: dict, client: boto3.client) -> list:
        """
        Gets the inventory data from the AWS big data service

        Args:
            info (dict): The info dictionary
            client (boto3.client): The boto3 client for AWS S3

        Returns:
            list: The inventory data
        """
        inv_obj = NoaaDownloader.__try_get_object(
            self.__big_data_bucket, info["inv"], client
        )
        inv_data_tmp = str(inv_obj["Body"].read().decode("utf-8")).split("\n")
        inv_data = []
        for line in inv_data_tmp:
            if not line == "":
                inv_data.append(line)
        byte_list = []
        for v in self.variables():
            byte_list.append(NoaaDownloader.__get_inventory_byte_list(inv_data, v))
        return byte_list

    def __get_grib_big_data(
        self, info: dict, s3_client: boto3.client
    ) -> Tuple[Union[str, None], int, int]:
        """
        Gets the grib file from the AWS big data service

        Args:
            info (dict): The info dictionary
            s3_client (boto3.client): The boto3 client for AWS S3

        Returns:
            str: The path to the grib file
        """
        import tempfile
        import os
        import logging

        logger = logging.getLogger(__name__)

        time = info["cycledate"]
        fn = info["grb"].rsplit("/")[-1]
        year = "{0:04d}".format(time.year)
        month = "{0:02d}".format(time.month)
        day = "{0:02d}".format(time.day)

        destination_folder = os.path.join(self.mettype(), year, month, day)
        local_file = os.path.join(tempfile.gettempdir(), fn)
        path_found = self.__database.has(self.mettype(), info)

        if not path_found:

            # ...Get the inventory data
            byte_list = self.__get_inventory_big_data(info, s3_client)
            if not len(byte_list) == len(self.variables()):
                logger.error(
                    "Could not gather the inventory or missing variables detected. Trying again later."
                )
                return None, 0, 1
            n = 1

            logger.info(
                "Downloading File: {:s} (F: {:s}, T: {:s})".format(
                    fn,
                    info["cycledate"].strftime("%Y-%m-%d %H:%M:%S"),
                    info["forecastdate"].strftime("%Y-%m-%d %H:%M:%S"),
                )
            )
            grb_key = info["grb"]
            with open(local_file, "wb") as fid:
                for r in byte_list:
                    if r:
                        return_range = "bytes=" + r["start"] + "-" + r["end"]
                        grb_obj = NoaaDownloader.__try_get_object(
                            self.__big_data_bucket, grb_key, s3_client, return_range
                        )
                        fid.write(grb_obj["Body"].read())

            # ...Used to check if we actually got some data
            file_size = os.path.getsize(local_file)

            # ...Name of the file in S3
            remote_file = destination_folder + "/" + fn

            if file_size > 0:
                self.s3file().upload_file(local_file, remote_file)
            else:
                remote_file = None
            os.remove(local_file)

            return remote_file, n, 0

        else:
            return None, 0, 0

    def __get_grib_noaa_servers(self, info: dict) -> Tuple[Union[str, None], int, int]:
        """
        Gets the grib based upon the input data

        Args:
            info (dict): variable containing the location of the data

        Returns:
            str: returns the name of the file that has been downloaded

        Pain and suffering this way lies, use the AWS big data option whenever
        available
        """
        import os.path
        import requests
        import tempfile
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        import logging

        logger = logging.getLogger(__name__)

        # ...Note: Status 302 is NOAA speak for "chill out", not a redirect as in normal http
        retry_strategy = Retry(
            total=20,
            redirect=6,
            backoff_factor=1.0,
            status_forcelist=[302, 429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
        )
        adaptor = HTTPAdapter(max_retries=retry_strategy)

        try:
            with requests.Session() as http:
                http.mount("https://", adaptor)
                http.mount("http://", adaptor)

                inv = http.get(info["inv"], timeout=30)
                inv.raise_for_status()
                if inv.status_code == 302:
                    logger.error("RESP: ", inv.text)
                inv_lines = str(inv.text).split("\n")
                retlist = []
                for v in self.variables():
                    retlist.append(
                        NoaaDownloader.__get_inventory_byte_list(inv_lines, v)
                    )

                if not len(retlist) == len(self.__variables):
                    logger.error(
                        "Could not gather the inventory or missing variables detected. Trying again later."
                    )
                    return None, 0, 1

                fn = info["grb"].rsplit("/")[-1]
                year = "{0:04d}".format(info["cycledate"].year)
                month = "{0:02d}".format(info["cycledate"].month)
                day = "{0:02d}".format(info["cycledate"].day)

                dfolder = os.path.join(self.mettype(), year, month, day)
                floc = os.path.join(tempfile.gettempdir(), fn)
                pathfound = self.__database.has(self.mettype(), info)

                if not pathfound:
                    logger.info(
                        "Downloading File: {:s} (F: {:s}, T: {:s})".format(
                            fn,
                            info["cycledate"].strftime("%Y-%m-%d %H:%M:%S"),
                            info["forecastdate"].strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    )
                    n = 1
                    total_size = 0
                    got_size = 0

                    for r in retlist:
                        headers = {
                            "Range": "bytes=" + str(r["start"]) + "-" + str(r["end"])
                        }

                        # ...Get the expected size of the download + 1 byte of http response metadata
                        total_size += int(r["end"]) - int(r["start"]) + 1
                        try:
                            with http.get(
                                info["grb"], headers=headers, stream=True, timeout=30
                            ) as req:
                                req.raise_for_status()
                                got_size += len(req.content)
                                with open(floc, "ab") as f:
                                    for chunk in req.iter_content(chunk_size=8192):
                                        f.write(chunk)
                        except KeyboardInterrupt:
                            raise
                        except:
                            logger.warning(
                                "NOAA Server stopped responding. Trying again later"
                            )
                            if os.path.exists(floc):
                                os.remove(floc)
                            return None, 0, 1

                    # ...Check that the full path was downloaded
                    delta_size = got_size - total_size
                    if delta_size != 0 and got_size > 0:
                        logger.error(
                            "Did not get the full file from NOAA. Trying again later."
                        )
                        os.remove(floc)
                        return None, 0, 0

                    file_size = os.path.getsize(floc)
                    remote_file = dfolder + "/" + fn

                    if file_size > 0:
                        self.__s3file.upload_file(floc, remote_file)
                    else:
                        remote_file = None
                    os.remove(floc)

                    return remote_file, n, 0
                else:
                    return None, 0, 0

        except KeyboardInterrupt:
            raise

    @staticmethod
    def _generate_prefix(date: datetime, hour: int) -> str:
        """
        Generates the prefix for the AWS big data files

        Args:
            date (datetime): date of the file
            hour (int): hour of the file

        Returns:
            str: prefix of the file

        This method is meant to be overridden by the child classes

        """
        raise RuntimeError("Override method not implemented")

    @staticmethod
    def _filename_to_hour(filename: str) -> int:
        """
        Converts the filename to the hour of the file

        Args:
            filename (str): filename of the file

        Returns:
            int: hour of the file

        This method is meant to be overridden by the child classes
        """
        raise RuntimeError("Override method not implemented")

    def _download_aws_big_data(self) -> int:
        """
        Downloads data from the AWS big data service

        Returns:
            int: number of files downloaded
        """
        s3 = boto3.resource("s3")
        client = boto3.client("s3")
        bucket = s3.Bucket(self.big_data_bucket())
        begin = datetime(
            self.begindate().year, self.begindate().month, self.begindate().day, 0, 0, 0
        )
        end = datetime(
            self.enddate().year, self.enddate().month, self.enddate().day, 0, 0, 0
        )
        date_range = [begin + timedelta(days=x) for x in range(0, (end - begin).days)]

        pairs = []
        for d in date_range:
            for h in self.cycles():
                prefix = self._generate_prefix(d, h)
                objects = bucket.objects.filter(Prefix=prefix)
                cycle_date = d + timedelta(hours=h)
                for o in objects:
                    if ".idx" in str(o):
                        continue
                    forecast_hour = self._filename_to_hour(o.key)
                    forecast_date = cycle_date + timedelta(hours=forecast_hour)
                    pairs.append(
                        {
                            "grb": o.key,
                            "inv": o.key + ".idx",
                            "cycledate": cycle_date,
                            "forecastdate": forecast_date,
                        }
                    )

        nerror = 0
        num_download = 0

        for p in pairs:
            if self.__do_archive:
                file_path, n, err = self.getgrib(p, client)
                nerror += err
                if file_path:
                    self.__database.add(p, self.mettype(), file_path)
                    num_download += n
            else:
                filepath = "s3://{:s}/{:s}".format(self.big_data_bucket(), p["grb"])
                if not self.__database.has(self.mettype(), p):
                    num_download += 1
                    self.__database.add(p, self.mettype(), filepath)

        return num_download

    def download(self) -> int:
        """
        Downloads the data from the NOAA server

        Returns:
            int: number of files downloaded
        """
        if self.__use_aws_big_data:
            return self._download_aws_big_data()
        else:
            raise RuntimeError("Override method not implemented")

    @staticmethod
    def linkToTime(t):
        """
        Converts a link in NOAA format to a datetime

        Args:
            t (str): Link to convert

        Returns:
            datetime: datetime object
        """

        if t[-1] == "/":
            dstr = t[1:-1].rsplit("/", 1)[-1]
        else:
            dstr = t.rsplit("/", 1)[-1]

        if len(dstr) == 4:
            return datetime(int(dstr), 1, 1)
        elif len(dstr) == 6:
            return datetime(int(dstr[0:4]), int(dstr[4:6]), 1)
        elif len(dstr) == 8:
            return datetime(int(dstr[0:4]), int(dstr[4:6]), int(dstr[6:8]))
        elif len(dstr) == 10:
            return datetime(
                int(dstr[0:4]), int(dstr[4:6]), int(dstr[6:8]), int(dstr[8:10]), 0, 0
            )
        else:
            raise Exception("Could not convert link to a datetime")
