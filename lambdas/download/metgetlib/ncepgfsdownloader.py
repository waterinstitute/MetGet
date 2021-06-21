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


class NcepGfsdownloader(NoaaDownloader):
    def __init__(self, begin, end):
        address = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
        NoaaDownloader.__init__(self, "gfs_ncep", "GFS-NCEP", address,
                                begin, end)
        self.__lastdate = self.begindate()

    def download(self):
        from .spyder import Spyder
        from datetime import datetime
        from .metdb import Metdb
        import hashlib

        num_download = 0
        s = Spyder(self.address())
        db = Metdb()
        lastdate = self.begindate()

        links = []
        day_links = s.filelist()
        for l in day_links:
            if "gfs." in l:
                dstr = l[0:-1].rsplit('/', 1)[-1].rsplit('.', 1)[-1]
                yr = int(dstr[0:4])
                mo = int(dstr[4:6])
                dy = int(dstr[6:8])
                t = datetime(yr, mo, dy, 0, 0, 0)
                if (self.enddate() >= t >= self.begindate()) and t >= self.__lastdate:
                    s2 = Spyder(l)
                    hr_links = s2.filelist()
                    lastdate = t
                    for ll in hr_links:
                        s3 = Spyder(ll+"atmos/")
                        files = s3.filelist()
                        for lll in files:
                            if ".pgrb2.0p25.f" in lll:
                                if "idx" not in lll:
                                    links.append(lll)

        pairs = self.generateGrbInvPairs(links)
        nerror = 0
        for p in pairs:
            fpath, n, err = self.getgrib(p, p["cycledate"])
            nerror += err
            if fpath:
                db.add(p, self.mettype(), fpath)
                num_download += n

        if nerror == 0:
            self.__lastdate = lastdate

        return num_download

    @staticmethod
    def generateGrbInvPairs(glist):
        from datetime import datetime
        from datetime import timedelta
        pairs = []
        for i in range(0, len(glist)):
            lst = glist[i].rsplit("/")
            v1 = lst[-1]
            v2 = lst[-3]
            v3 = lst[-4].rsplit(".", 1)[-1]

            yr = int(v3[0:4])
            mo = int(v3[4:6])
            dy = int(v3[6:8])
            cycle = int(v2)
            fcst = int(v1[-3:])

            cdate = datetime(yr, mo, dy, cycle, 0, 0)
            fdate = cdate + timedelta(hours=fcst)
            pairs.append({
                "grb": glist[i],
                "inv": glist[i] + ".idx",
                "cycledate": cdate,
                "forecastdate": fdate
            })
        return pairs
