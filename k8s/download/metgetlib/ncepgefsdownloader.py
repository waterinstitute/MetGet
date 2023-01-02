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

from .noaadownloader import NoaaDownloader


class NcepGefsdownloader(NoaaDownloader):
    def __init__(self, begin, end):
        address = None
        NoaaDownloader.__init__(
            self, "gefs_ncep", "GEFS-NCEP", address, begin, end, use_aws_big_data=True
        )
        self.add_download_variable("PRMSL", "press"),
        self.add_download_variable("ICETK:surface", "ice")
        self.add_download_variable("APCP", "accumulated_precip")
        self.add_download_variable("RH:2 m above ground", "humidity")
        self.add_download_variable("TMP:2 m above ground", "temperature")
        self.set_big_data_bucket("noaa-gefs-pds")
        self.set_cycles([0, 6, 12, 18])

        # ...GEFS ensemble members:
        #   Valid perturbations for gefs are:
        #   avg => ensemble mean
        #   c00 => control
        #   pXX => perturbation XX (1-30)
        self.__members = ["avg", "c00"]
        for i in range(30):
            self.__members.append("p{:02d}".format(i + 1))

    def members(self) -> list:
        return self.__members

    @staticmethod
    def _generate_prefix(date, hour) -> str:
        return (
            "gefs." + date.strftime("%Y%m%d") + "/{:02d}/atmos/pgrb2sp25/g".format(hour)
        )

    @staticmethod
    def _filename_to_hour(filename) -> int:
        return int(filename[-3:])

    # ...In the case of GEFS, we need to reimplement this function because we have to deal with ensemble members
    def _download_aws_big_data(self):
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
                for obj in objects:
                    if obj.key[-4:] == ".idx":
                        continue

                    keys = obj.key.split("/")
                    member = keys[4][2:5]
                    if member not in self.members():
                        continue

                    forecast_hour = self._filename_to_hour(obj.key)
                    forecast_date = cycle_date + timedelta(hours=forecast_hour)
                    pairs.append(
                        {
                            "grb": obj.key,
                            "inv": obj.key + ".idx",
                            "cycledate": cycle_date,
                            "forecastdate": forecast_date,
                            "ensemble_member": member,
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
