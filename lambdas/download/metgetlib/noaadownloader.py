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
    def __init__(self,
                 mettype,
                 metstring,
                 address,
                 begin,
                 end,
                 use_rainfall=False,
                 use_aws=True):
        """
        Constructor for the NoaaDownloader class. Initializes the
        :param mettype: Type of metetrology that is to be downloaded
        :param address: Server address
        :param begin: start date for downloaded
        :param end: end date for downloading
        """
        from .metdb import Metdb
        self.__mettype = mettype
        self.__metstring = metstring
        self.__address = address
        self.__beginDate = begin
        self.__endDate = end
        self.__use_aws = use_aws
        self.__database = Metdb()

        if self.__use_aws:
            from .s3file import S3file
            self.__s3file = S3file()

        # The following variables will be used. Presently, these are the
        # variables that ADCIRC can support (wind vector, pressure, and ice)
        if use_rainfall:
            self.__variables = [{
                "long_name": "UGRD:10 m above ground",
                "name": "uvel"
            }, {
                "long_name": "VGRD:10 m above ground",
                "name": "vvel"
            }, {
                "long_name": "PRMSL",
                "name": "press"
            }, {
                "long_name": "APCP",
                "name": "precip"
            }, {
                "long_name": "ICEC:surface",
                "name": "ice"
            }]
        else:
            self.__variables = [{
                "long_name": "UGRD:10 m above ground",
                "name": "uvel"
            }, {
                "long_name": "VGRD:10 m above ground",
                "name": "vvel"
            }, {
                "long_name": "PRMSL",
                "name": "press"
            }, {
                "long_name": "ICEC:surface",
                "name": "ice"
            }]

    def mettype(self):
        return self.__mettype

    def metstring(self):
        return self.__metstring

    def address(self):
        return self.__address

    def database(self):
        return self.__database

    def dynamo(self):
        return self.__dynamo

    def begindate(self):
        return self.__beginDate

    def enddate(self):
        return self.__endDate

    def setbegindate(self, date):
        self.__beginDate = date

    def setenddate(self, date):
        self.__endDate = date

    def use_aws(self):
        return self.__use_aws

    def getgrib(self, info, time):
        """
        Gets the grib based upon the input data
        :param folder: folder to place the data
        :param info: variable containing the location of the data
        :param time: time that the data represents
        :return: returns the name of the file that has been downloaded
        """
        import os.path
        import requests
        import tempfile

        n = 0
        try:
            inv = requests.get(info['inv'], stream=True, timeout=30)
            inv_lines = str(inv.text).split("\n")
            retlist = []
            for i in range(len(inv_lines)):
                for v in self.__variables:
                    if v["long_name"] in inv_lines[i]:
                        startbits = inv_lines[i].split(":")[1]
                        endbits = inv_lines[i + 1].split(":")[1]
                        retlist.append({"name": v["name"], "start": startbits, "end": endbits})
                        break

            fn = info['grb'].rsplit("/")[-1]
            year = "{0:04d}".format(time.year)
            month = "{0:02d}".format(time.month)
            day = "{0:02d}".format(time.day)

            dfolder = self.mettype() + "/" + year + "/" + month + "/" + day
            floc = tempfile.gettempdir() + "/" + fn
            pathfound = self.__s3file.exists(dfolder + "/" + fn)

            if not pathfound:
                print("     Downloading File: " + fn + " (F: " + info["cycledate"].strftime("%Y-%m-%d %H:%M:%S") +
                      ", T: " + info["forecastdate"].strftime("%Y-%m-%d %H:%M:%S") + ")", flush=True)
                n = 1
                for r in retlist:
                    headers = {"Range": "bytes=" + str(r["start"]) + "-" + str(r["end"])}
                    try:
                        with requests.get(info['grb'], headers=headers, stream=True, timeout=30) as req:
                            req.raise_for_status()
                            with open(floc, 'ab') as f:
                                for chunk in req.iter_content(chunk_size=8192):
                                    f.write(chunk)
                    except KeyboardInterrupt:
                        raise
                    except:
                        print("    [WARNING]: NOAA Server stopped responding. Trying again later")
                        if os.path.exists(floc):
                            os.remove(floc)
                        return None, 0, 1

                self.__s3file.upload_file(floc, dfolder + "/" + fn)
                os.remove(floc)
                return dfolder + "/" + fn, n, 0
            else:
                return None, 0, 0

        except KeyboardInterrupt:
            raise
        except:
            print("[WARNING]: NOAA Server stopped responding. Trying again later")
            return None, 0, 1

    def download(self):
        raise RuntimeError("Method not implemented")

    @staticmethod
    def linkToTime(t):
        """
        Converts a link in NOAA format to a datetime
        :param t: Link to convert
        :return: datetime object
        """
        from datetime import datetime
        if t[-1] == "/":
            dstr = t[1:-1].rsplit('/', 1)[-1]
        else:
            dstr = t.rsplit('/', 1)[-1]

        if len(dstr) == 4:
            return datetime(int(dstr), 1, 1)
        elif len(dstr) == 6:
            return datetime(int(dstr[0:4]), int(dstr[4:6]), 1)
        elif len(dstr) == 8:
            return datetime(int(dstr[0:4]), int(dstr[4:6]), int(dstr[6:8]))
        elif len(dstr) == 10:
            return datetime(int(dstr[0:4]), int(dstr[4:6]), int(dstr[6:8]),
                            int(dstr[8:10]), 0, 0)
        else:
            raise Exception("Could not convert link to a datetime")