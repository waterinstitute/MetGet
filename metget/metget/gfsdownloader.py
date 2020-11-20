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


class Gfsdownloader(NoaaDownloader):
    def __init__(self, dblocation, begin, end):
        address = "https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-004-0.5-degree/forecast/"
        NoaaDownloader.__init__(self, "gfs_fcst", "GFS", address, dblocation,
                                begin, end)
        self.__downloadlocation = dblocation + "/" + self.mettype()

    def download(self):
        from metget.spyder import Spyder
        from datetime import datetime
        from metget.metdb import Metdb
        import os.path
        num_download = 0
        s = Spyder(self.address())
        db = Metdb(self.dblocation())

        month_links = s.filelist()
        for l in month_links:
            dmin2 = datetime(self.begindate().year,
                             self.begindate().month, 1, 0, 0, 0)
            t = self.linkToTime(l)
            if t >= dmin2:
                print("Processing directory for month: ", t.year, '-', t.month)
                s2 = Spyder(l)
                day_links = s2.filelist()
                for ll in day_links:
                    t2 = self.linkToTime(ll)

                    if t2 < self.begindate() or t2 > self.enddate():
                        continue

                    print("    Processing directory for day: ", t2.year, '-',
                          t2.month, '-', t2.day)
                    s3 = Spyder(ll)
                    file_links = s3.filelist()
                    pairs = self.generateGrbInvPairs(file_links)
                    for p in pairs:
                        fpath, n, _ = self.getgrib(self.__downloadlocation, p, t2)
                        db.add(p, self.mettype(), fpath)
                        num_download += n

        return num_download

    @staticmethod
    def generateGrbInvPairs(glist):
        from datetime import datetime
        from datetime import timedelta
        pairs = []
        for i in range(0, len(glist), 2):
            v2 = glist[i].rsplit("/", 1)[-1]
            cyear = int(v2[6:10])
            cmon = int(v2[10:12])
            cday = int(v2[12:14])
            chour = int(v2[15:17])
            fhour = int(v2[20:23])
            cdate = datetime(cyear, cmon, cday, chour, 0, 0)
            fdate = cdate + timedelta(hours=fhour)

            if len(glist) >= i + 2:
                pairs.append({
                    "grb": glist[i],
                    "inv": glist[i + 1],
                    "cycledate": cdate,
                    "forecastdate": fdate
                })
        return pairs
