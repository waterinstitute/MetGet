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

from metget.noaadownloader import NoaaDownloader


class Hwrfdownloader(NoaaDownloader):
    def __init__(self, dblocation, begin, end):
        address = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hur/prod/"
        NoaaDownloader.__init__(self, "hwrf", "HWRF", address, dblocation,
                                begin, end)
        self.__downloadlocation = dblocation + "/" + self.mettype()

    def download(self):
        from metget.spyder import Spyder
        from metget.metdb import Metdb
        num_download = 0
        s = Spyder(self.address())
        db = Metdb(self.dblocation())

        links = s.filelist()
        files = []
        for l in links:
            if "hwrf." in l:
                s2 = Spyder(l)
                l2 = s2.filelist()
                for ll in l2:
                    if "hwrfprs.storm" in ll:
                        if "idx" not in ll:
                            files.append(ll)
        pairs = self.generateGrbInvPairs(files)
        for p in pairs:
            fpath, n, _ = self.getgrib(self.__downloadlocation, p, p["cycledate"])
            if fpath:
                db.add(p, self.mettype(), fpath)
                num_download = num_download + n

        return num_download

    @staticmethod
    def generateGrbInvPairs(glist):
        from datetime import datetime
        from datetime import timedelta
        pairs = []
        for i in range(0, len(glist)):
            v2 = glist[i].rsplit("/", 1)[-1]
            v3 = v2.rsplit(".")[1]
            v4 = v2.rsplit(".")[5][1:4]
            name = v2.rsplit(".")[0]
            cyear = int(v3[0:4])
            cmon = int(v3[4:6])
            cday = int(v3[6:8])
            chour = int(v3[8:10])
            fhour = int(v4)
            cdate = datetime(cyear, cmon, cday, chour, 0, 0)
            fdate = cdate + timedelta(hours=fhour)
            pairs.append({
                "name": name,
                "grb": glist[i],
                "inv": glist[i] + ".idx",
                "cycledate": cdate,
                "forecastdate": fdate
            })
        return pairs
