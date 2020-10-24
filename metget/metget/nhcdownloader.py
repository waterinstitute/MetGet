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

class NhcDownloader:
    def __init__(self, dblocation, use_besttrack=True, use_forecast=True):
        from datetime import datetime
        from metget.metdb import Metdb
        self.__dblocation = dblocation
        self.__downloadlocation = dblocation + "/nhc"
        self.__mettype = "nhc"
        self.__metstring = "NHC"
        self.__use_forecast = use_besttrack
        self.__use_hindcast = use_forecast
        self.__year = datetime.now().year
        self.__database = Metdb(self.__dblocation)

    def mettype(self):
        return self.__mettype

    def metstring(self):
        return self.__metstring

    def download(self):
        n = 0
        if self.__use_forecast:
            n += self.download_forecast()
        if self.__use_hindcast:
            n += self.download_hindcast()
        return n

    def download_forecast(self):
        from ftplib import FTP
        import os.path

        ftp = FTP('ftp.nhc.noaa.gov')
        ftp.login()
        ftp.cwd('atcf/fst')
        filelist = ftp.nlst("*.fst")

        n = 0

        for f in filelist:
            year = f[4:8]
            if int(year) == self.__year:
                basin = f[0:2]
                storm = f[2:4]
                site = self.generate_storm_forecast_homepage_url(year, basin, storm)
                advlist = self.get_advisories(site)
                if advlist:
                    latest_advisory = advlist[-1]
                    filepath = self.__downloadlocation + "_fcst/nhc_fcst_" + year + "_" + basin + \
                               "_" + storm + "_" + "{:03d}".format(latest_advisory) + ".btk"
                    if not os.path.exists(filepath):
                        print(
                            "    Downloading NHC forecast for Basin: " + basin2string(basin) + ", Year: " +
                            str(year) + ", Storm: " + str(storm) + ", Advisory: " + str(latest_advisory), flush=True)
                        ftp.retrbinary("RETR " + f, open(filepath, 'wb').write)
                        start_date, end_date, duration = self.get_nhc_start_end_date(filepath, True)
                        data = {"year": int(year), "basin": basin, "storm": int(storm), "advisory": latest_advisory,
                                'advisory_start': start_date, 'advisory_end': end_date,
                                'advisory_duration_hr': duration}
                        self.__database.add(data, "nhc_fcst", filepath)
                        n += 1
        return n

    def download_hindcast(self):
        from ftplib import FTP
        import os.path

        # Anonymous FTP login
        try: 
            ftp = FTP('ftp.nhc.noaa.gov')
            ftp.login()
            ftp.cwd('atcf/btk')
            filelist = ftp.nlst("*.dat")
        except:
            return 0

        n = 0

        # Iterate through files and find the associated advisory
        for f in filelist:
            year = f[5:9]
            if int(year) == self.__year:
                basin = f[1:3]
                storm = f[3:5]
                site = self.generate_storm_forecast_homepage_url(year, basin, storm)
                advlist = self.get_advisories(site)
                if advlist:
                    latest_advisory = advlist[-1]
                    filepath = self.__downloadlocation + "_btk/nhc_btk_" + year + "_" + basin + \
                               "_" + storm + "_" + "{:03d}".format(latest_advisory) + ".btk"
                    if not os.path.exists(filepath):
                        print(
                            "    Downloading NHC best track for Basin: " + basin2string(basin) + ", Year: " +
                            str(year) + ", Storm: " + str(storm) + ", Advisory: " + str(latest_advisory), flush=True)
                        ftp.retrbinary("RETR " + f, open(filepath, 'wb').write)
                        start_date, end_date, duration = self.get_nhc_start_end_date(filepath, False)
                        data = {"year": int(year), "basin": basin, "storm": int(storm), "advisory": latest_advisory,
                                'advisory_start': start_date, 'advisory_end': end_date,
                                'advisory_duration_hr': duration}
                        self.__database.add(data, "nhc_btk", filepath)
                        n += 1
        return n

    @staticmethod
    def generate_storm_forecast_homepage_url(year, basin, storm):
        return "https://www.nhc.noaa.gov/archive/" + year + "/" + basin + storm

    @staticmethod
    def get_advisories(url):
        import requests
        from bs4 import BeautifulSoup
        try:
            r = requests.get(url, timeout=10)
            if r.ok:
                response_text = r.text
            else:
                return []
        except KeyboardInterrupt:
            raise
        except:
            return []

        soup = BeautifulSoup(response_text, 'html.parser')
        advisories = []
        for node in soup.find_all('a'):
            linkaddr = node.get('href')
            if linkaddr and "fstadv" in linkaddr:
                try:
                    advisories.append(int(linkaddr[-10:-7]))
                except ValueError: 
                    continue


        return advisories

    @staticmethod
    def get_nhc_start_end_date(filename, is_forecast):
        from datetime import datetime, timedelta
        import csv
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            line = 0
            for l in reader:
                if line == 0:
                    firstline = l
                else:
                    lastline = l
                line += 1

        start_date = datetime.strptime(str.strip(firstline[2]), "%Y%m%d%H")
        if is_forecast:
            duration = int(lastline[5])
            end_date = start_date + timedelta(hours=duration)
        else:
            end_date = datetime.strptime(str.strip(lastline[2]), "%Y%m%d%H")
            duration = (end_date - start_date).total_seconds() / 3600

        return start_date, end_date, duration


def basin2string(basin_abbrev):
    if basin_abbrev == "ep":
        return "Eastern Pacific"
    elif basin_abbrev == "al":
        return "Atlantic"
    elif basin_abbrev == "cp":
        return "Central Pacific"
    return basin_abbrev
