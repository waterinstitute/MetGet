#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 ADCIRC Development Group
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
"""
Parent class for downloading noaa grib format data
"""


class NoaaDownloader:
    def __init__(
        self,
        mettype,
        metstring,
        address,
        begin,
        end,
        use_aws=True,
        use_aws_big_data=False,
    ):
        """
        Constructor for the NoaaDownloader class. Initializes the
        :param mettype: Type of metetrology that is to be downloaded
        :param address: Server address
        :param begin: start date for downloaded
        :param end: end date for downloading
        """
        from .metdb import Metdb
        import os

        self.__mettype = mettype
        self.__metstring = metstring
        self.__address = address
        self.__beginDate = begin
        self.__endDate = end
        self.__use_aws = use_aws
        self.__database = Metdb()
        self.__use_aws_big_data = use_aws_big_data
        self.__big_data_bucket = None
        self.__cycles = None

        if self.__use_aws:
            from .s3file import S3file

            if "BUCKET_NAME" in os.environ:
                self.__s3file = S3file(os.environ["BUCKET_NAME"])
            else:
                self.__s3file = S3file()

        # The default variable list. Must haves for
        #   this system at present
        self.__variables = [
            {"long_name": "UGRD:10 m above ground", "name": "uvel"},
            {"long_name": "VGRD:10 m above ground", "name": "vvel"},
            {"long_name": "PRMSL", "name": "press"},
        ]

    def s3file(self):
        return self.__s3file

    def use_aws(self):
        return self.__use_aws

    def set_cycles(self, cycle_list):
        self.__cycles = cycle_list

    def cycles(self):
        return self.__cycles

    def set_big_data_bucket(self, bucket_name):
        self.__big_data_bucket = bucket_name

    def big_data_bucket(self):
        return self.__big_data_bucket

    def use_big_data(self):
        return self.__use_aws_big_data

    def add_download_variable(self, long_name, name):
        self.__variables.append({"long_name": long_name, "name": name})

    def variables(self):
        return self.__variables

    def mettype(self):
        return self.__mettype

    def metstring(self):
        return self.__metstring

    def address(self):
        return self.__address

    def database(self):
        return self.__database

    def begindate(self):
        return self.__beginDate

    def enddate(self):
        return self.__endDate

    def setbegindate(self, date):
        self.__beginDate = date

    def setenddate(self, date):
        self.__endDate = date

    def getgrib(self, info, client=None):
        if self.use_big_data():
            if client is None:
                raise RuntimeError(
                    "Need client for getgrib when using AWS big data service"
                )
            return self.__get_grib_big_data(info, client)
        else:
            return self.__get_grib_noaa_servers(info)

    @staticmethod
    def __get_inventory_byte_list(inventory_data, variable):
        for i in range(len(inventory_data)):
            if variable["long_name"] in inventory_data[i]:
                start_bits = inventory_data[i].split(":")[1]
                end_bits = inventory_data[i + 1].split(":")[1]
                return {"name": variable["name"], "start": start_bits, "end": end_bits}

    def __get_inventory_big_data(self, info, client):
        inv_obj = client.get_object(Bucket=self.__big_data_bucket, Key=info["inv"])
        inv_data = str(inv_obj["Body"].read().decode("utf-8")).split("\n")
        byte_list = []
        for v in self.variables():
            byte_list.append(NoaaDownloader.__get_inventory_byte_list(inv_data, v))
        return byte_list

    def __get_grib_big_data(self, info, s3_client):
        import tempfile
        import os

        byte_list = self.__get_inventory_big_data(info, s3_client)
        if not len(byte_list) == len(self.variables()):
            print(
                "[ERROR]: Could not gather the inventory or missing variables detected. Trying again later."
            )
            return None, 0, 1

        time = info["cycledate"]
        fn = info["grb"].rsplit("/")[-1]
        year = "{0:04d}".format(time.year)
        month = "{0:02d}".format(time.month)
        day = "{0:02d}".format(time.day)

        destination_folder = self.mettype() + "/" + year + "/" + month + "/" + day
        local_file = tempfile.gettempdir() + "/" + fn

        if self.use_aws():
            path_found = self.s3file().exists(destination_folder + "/" + fn)
        else:
            path_found = os.path.exists(fn)

        if not path_found:
            n = 1
            print(
                "     Downloading File: "
                + fn
                + " (F: "
                + info["cycledate"].strftime("%Y-%m-%d %H:%M:%S")
                + ", T: "
                + info["forecastdate"].strftime("%Y-%m-%d %H:%M:%S")
                + ")",
                flush=True,
            )
            grb_key = info["grb"]
            with open(local_file, "wb") as fid:
                for r in byte_list:
                    return_range = "bytes=" + r["start"] + "-" + r["end"]
                    grb_obj = s3_client.get_object(
                        Bucket=self.__big_data_bucket, Key=grb_key, Range=return_range
                    )
                    fid.write(grb_obj["Body"].read())
            if self.use_aws():
                self.s3file().upload_file(local_file, destination_folder + "/" + fn)
                os.remove(local_file)
            else:
                os.rename(local_file, fn)

            return destination_folder + "/" + fn, n, 0

        else:
            return None, 0, 0

    def __get_grib_noaa_servers(self, info):
        """
        Gets the grib based upon the input data
        :param info: variable containing the location of the data
        :return: returns the name of the file that has been downloaded

        Pain and suffering this way lies, use the AWS big data option whenever
        available

        """
        import os.path
        import requests
        import tempfile
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        # ...Note: Status 302 is NOAA speak for "chill out", not a redirect as in normal http
        retry_strategy = Retry(
            total=20,
            redirect=6,
            backoff_factor=1.0,
            status_forcelist=[302, 429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
        )
        adaptor = HTTPAdapter(max_retries=retry_strategy)

        n = 0
        try:
            with requests.Session() as http:
                http.mount("https://", adaptor)
                http.mount("http://", adaptor)

                inv = http.get(info["inv"], timeout=30)
                inv.raise_for_status()
                if inv.status_code == 302:
                    print("RESP: ", inv.text)
                inv_lines = str(inv.text).split("\n")
                retlist = []
                for v in self.variables():
                    retlist.append(
                        NoaaDownloader.__get_inventory_byte_list(inv_lines, v)
                    )

                if not len(retlist) == len(self.__variables):
                    print(
                        "[ERROR]: Could not gather the inventory or missing variables detected. Trying again later."
                    )
                    return None, 0, 1

                fn = info["grb"].rsplit("/")[-1]
                year = "{0:04d}".format(info["cycledate"].year)
                month = "{0:02d}".format(info["cycledate"].month)
                day = "{0:02d}".format(info["cycledate"].day)

                dfolder = self.mettype() + "/" + year + "/" + month + "/" + day
                floc = tempfile.gettempdir() + "/" + fn

                if self.__use_aws:
                    pathfound = self.__s3file.exists(dfolder + "/" + fn)
                else:
                    pathfound = os.path.exists(fn)

                if not pathfound:
                    print(
                        "     Downloading File: "
                        + fn
                        + " (F: "
                        + info["cycledate"].strftime("%Y-%m-%d %H:%M:%S")
                        + ", T: "
                        + info["forecastdate"].strftime("%Y-%m-%d %H:%M:%S")
                        + ")",
                        flush=True,
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
                            print(
                                "    [WARNING]: NOAA Server stopped responding. Trying again later"
                            )
                            if os.path.exists(floc):
                                os.remove(floc)
                            return None, 0, 1

                    # ...Check that the full path was downloaded
                    delta_size = got_size - total_size
                    if delta_size != 0 and got_size > 0:
                        print(
                            "[ERROR]: Did not get the full file from NOAA. Trying again later."
                        )
                        os.remove(floc)
                        return None, 0, 0

                    if self.__use_aws:
                        self.__s3file.upload_file(floc, dfolder + "/" + fn)
                        os.remove(floc)
                    else:
                        os.rename(floc, fn)

                    return dfolder + "/" + fn, n, 0
                else:
                    return None, 0, 0

        except KeyboardInterrupt:
            raise
        # except:
        #    print("[WARNING]: NOAA Server stopped responding. Trying again later")
        #    return None, 0, 1

    @staticmethod
    def _generate_prefix(date, hour) -> str:
        raise RuntimeError("Override method not implemented")

    @staticmethod
    def _filename_to_hour(filename) -> int:
        raise RuntimeError("Override method not implemented")

    def __download_aws_big_data(self):
        import boto3
        from .metdb import Metdb
        from datetime import datetime
        from datetime import timedelta

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
        db = Metdb()

        for p in pairs:
            file_path, n, err = self.getgrib(p, client)
            nerror += err
            if file_path:
                db.add(p, self.mettype(), file_path)
                num_download += n

        return num_download

    def download(self):
        if self.__use_aws_big_data:
            return self.__download_aws_big_data()
        else:
            raise RuntimeError("Override method not implemented")

    @staticmethod
    def linkToTime(t):
        """
        Converts a link in NOAA format to a datetime
        :param t: Link to convert
        :return: datetime object
        """
        from datetime import datetime

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
