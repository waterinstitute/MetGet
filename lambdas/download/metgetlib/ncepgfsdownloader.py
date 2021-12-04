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
        self.add_download_variable("ICEC:surface", "ice")
        self.add_download_variable("PRATE", "precip_rate")
        self.add_download_variable("RH:30-0 mb above ground", "humidity")
        self.add_download_variable("TMP:30-0 mb above ground", "temperature")

    def __generate_prefix(self, date, hour):
        return "gfs."+date.strftime("%Y%m%d")+"/{:02d}/atmos/gfs.t{:02d}z.pgrb2.0p25.f".format(hour,hour)

    def download(self):
        import boto3
        from .metdb import Metdb
        from datetime import datetime
        from datetime import timedelta
        bucket_name = "noaa-gfs-bdp-pds"
        s3 = boto3.resource("s3")
        client = boto3.client("s3")
        bucket = s3.Bucket(bucket_name)
        begin = datetime(self.begindate().year, self.begindate().month, self.begindate().day,0,0,0)
        end = datetime(self.enddate().year, self.enddate().month, self.enddate().day,0,0,0)
        date_range = [begin + timedelta(days=x) for x in range (0,(end-begin).days)]

        gfs_cycles = [ 0, 6, 12, 18]
        pairs = []
        for d in date_range:
            for h in gfs_cycles:
                prefix = self.__generate_prefix(d,h)
                objects = bucket.objects.filter(Prefix=prefix)
                cycle_date = d + timedelta(hours=h)
                for o in objects:
                    if ".idx" in str(o):
                        continue
                    f = int(o.key[-3:])
                    forecast_date = cycle_date + timedelta(hours=f)
                    pairs.append({
                        "grb": o.key,
                        "inv": o.key + ".idx",
                        "cycledate": cycle_date,
                        "forecastdate": forecast_date
                    })

        nerror = 0
        num_download = 0
        db = Metdb()

        for p in pairs:
            fpath, n, err = self.getgrib(p, client, bucket_name)
            nerror += err
            if fpath:
                db.add(p, self.mettype(), fpath)
                num_download += n

        return num_download


    def getgrib(self, info, client, bucket_name):
        import tempfile
        import os
        inv_key = info["inv"]
        grb_key = info["grb"]
        inv_obj = client.get_object(Bucket=bucket_name, Key=inv_key)
        inv_data = str(inv_obj["Body"].read().decode('utf-8')).split("\n")
        retlist=[]
        for v in self.variables():
            for i in range(len(inv_data)):
                if v["long_name"] in inv_data[i]:
                    startbits = inv_data[i].split(":")[1]
                    endbits = inv_data[i+1].split(":")[1]
                    retlist.append({"name": v["name"], "start": startbits, "end": endbits})
                    break
        if not len(retlist) == len(self.variables()):
            print("[ERROR]: Could not gather the inventory or missing variables detected. Trying again later.")
            return None, 0, 1

        time = info["cycledate"]
        fn = info['grb'].rsplit("/")[-1]
        year = "{0:04d}".format(time.year)
        month = "{0:02d}".format(time.month)
        day = "{0:02d}".format(time.day)

        dfolder = self.mettype() + "/" + year + "/" + month + "/" + day
        floc = tempfile.gettempdir() + "/" + fn

        if self.use_aws():
            pathfound = self.s3file().exists(dfolder+"/"+fn)
        else:
            pathfound = os.path.exists(fn)

        if not pathfound:
            n = 1
            print("     Downloading File: " + fn + " (F: " + info["cycledate"].strftime("%Y-%m-%d %H:%M:%S") +
                ", T: " + info["forecastdate"].strftime("%Y-%m-%d %H:%M:%S") + ")", flush=True)
            with open(floc,'wb') as fid:
                for r in retlist:
                    retrange = "bytes="+r["start"]+"-"+r["end"]
                    grb_obj = client.get_object(Bucket=bucket_name,Key=grb_key,Range=retrange)
                    fid.write(grb_obj["Body"].read())
            if self.use_aws():
                self.s3file().upload_file(floc, dfolder+"/"+fn)
                os.remove(floc)
            else:
                os.rename(floc,fn)

            return dfolder+"/"+fn, n, 0

        else:
            return None, 0, 0

