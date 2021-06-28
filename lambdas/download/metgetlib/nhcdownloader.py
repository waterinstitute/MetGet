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
    def __init__(self,
                 dblocation=".",
                 use_besttrack=True,
                 use_forecast=True,
                 pressure_method="knaffzehr",
                 use_aws=True):
        from datetime import datetime
        from .metdb import Metdb
        import tempfile

        self.__mettype = "nhc"
        self.__metstring = "NHC"
        self.__use_forecast = use_besttrack
        self.__use_hindcast = use_forecast
        self.__year = datetime.now().year
        self.__pressure_method = pressure_method
        self.__use_rss = True
        self.__use_aws = use_aws
        self.__database = Metdb()

        if self.__use_aws:
            from .s3file import S3file
            import os
            self.__dblocation = tempfile.gettempdir()
            self.__downloadlocation = dblocation + "/nhc"
            if "BUCKET_NAME" in os.environ:
                self.__s3file = S3file(os.environ["BUCKET_NAME"])
            else:
                self.__s3file = S3file()
        else:
            self.__dblocation = dblocation
            self.__downloadlocation = self.__dblocation + "/nhc"

        self.__rss_feeds = [
            "https://www.nhc.noaa.gov/index-at.xml",
            "https://www.nhc.noaa.gov/index-ep.xml",
            "https://www.nhc.noaa.gov/index-cp.xml"
        ]

    def mettype(self):
        return self.__mettype

    def metstring(self):
        return self.__metstring
        return self.__metstring

    def download(self):
        n = 0
        if self.__use_forecast:
            n += self.download_forecast()
        if self.__use_hindcast:
            n += self.download_hindcast()
        return n

    def download_forecast(self):
        if self.__use_rss:
            return self.download_forecast_rss()
        else:
            return self.download_forecast_ftp()

    def download_forecast_rss(self):
        print("[INFO]: Retrieving NHC RSS feed...")
        n = 0
        for feed in self.__rss_feeds:
            n += self.read_nhc_rss_feed(feed)

        print("[INFO]: Finished reading RSS feed")
        return n

    def read_nhc_rss_feed(self, rss):
        import feedparser
        import os
        from .forecastdata import ForecastData

        try:
            n = 0
            feed = feedparser.parse(rss)
            for e in feed.entries:
                if "Forecast Advisory" in e['title']:
                    adv_number = "{:03d}".format(int(e['title'].split()[-1]))
                    adv_lines = e["description"].split("\n")
                    id_str = (adv_lines[7].split()[-1]).lstrip()
                    basin_str = id_str[0:2]
                    storm_str = id_str[2:4]
                    year_str = id_str[-4:]
                    vmax = 0

                    storm_name = e['title'].split(
                        "Forecast Advisory")[0].split()[-1]
                    # storm_type = e['title'].split(storm_name)[0]

                    fn = "nhc_fcst_" + year_str + "_" + basin_str + "_" + storm_str + "_" + adv_number + ".fcst"
                    if self.__use_aws:
                        filepath = self.mettype() + "/forecast/" + fn
                        pathfound = self.__s3file.exists(filepath)
                    else:
                        filepath = self.__downloadlocation + "_fcst/" + fn
                        pathfound = os.path.exists(filepath)

                    if not pathfound:
                        print("    Downloading NHC forecast for Basin: " +
                              basin2string(basin_str) + ", Year: " + year_str +
                              ", Storm: " + storm_name + "(" + storm_str +
                              "), Advisory: " + adv_number,
                              flush=True)
                        i = 0
                        forecasts = [ForecastData(self.__pressure_method)]
                        while i < len(adv_lines):
                            if "CENTER LOCATED NEAR" in adv_lines[i] and "REPEAT" not in adv_lines[i]:
                                data = adv_lines[i].split("...")[0].split()
                                x, y = self.get_storm_center(data[-3], data[-4])
                                time = self.get_rss_time(data[-1])
                                forecasts[0].set_storm_center(x, y)
                                forecasts[0].set_time(time)
                            elif "ESTIMATED MINIMUM CENTRAL" in adv_lines[i]:
                                forecasts[0].set_pressure(
                                    float(adv_lines[i].split()[-2]))
                            elif "MAX SUSTAINED WINDS" in adv_lines[i]:
                                data = adv_lines[i].split()
                                if len(data) > 5:
                                    forecasts[0].set_max_gust(float(data[-2]))
                                forecasts[0].set_max_wind(float(data[3]))
                                vmax = forecasts[0].max_wind()
                                while "KT" in adv_lines[i + 1]:
                                    i += 1
                                    iso, d1, d2, d3, d4 = self.parse_isotachs(
                                        adv_lines[i])
                                    forecasts[0].set_isotach(iso, d1, d2, d3, d4)
                            elif "PRESENT MOVEMENT TOWARD" in adv_lines[i]:
                                heading = int(
                                    adv_lines[i].split("DEGREES")[0].split()[-1])
                                fwdspd = int(adv_lines[i].split()[-2])
                                forecasts[0].set_heading(heading)
                                forecasts[0].set_forward_speed(fwdspd)
                            elif "FORECAST VALID" in adv_lines[i] and "ABSORBED" not in adv_lines[i]:
                                data = adv_lines[i].split("...")[0].split()

                                # This should be specified in the rss, but if not, compute a value before going further
                                if forecasts[0].pressure() == -1:
                                    forecasts[0].compute_pressure()

                                if len(data) >= 4:
                                    forecasts.append(
                                        ForecastData(self.__pressure_method))
                                    data = adv_lines[i].split("...")[0].split()
                                    time = self.get_rss_time(data[2])
                                    x, y = self.get_storm_center(data[4], data[3])
                                    i += 1
                                    data = adv_lines[i].replace(".", " ").split()
                                    forecasts[-1].set_max_wind(float(data[2]))
                                    vmax = max(vmax, forecasts[-1].max_wind())
                                    forecasts[-1].set_max_gust(float(data[5]))

                                    forecasts[-1].set_storm_center(x, y)
                                    forecasts[-1].set_time(time)
                                    forecasts[-1].set_forecast_hour(
                                        (time -
                                         forecasts[0].time()).total_seconds() /
                                        3600)
                                    forecasts[-1].compute_pressure(
                                        vmax, forecasts[-2].max_wind(),
                                        forecasts[-2].pressure())

                                    while "KT" in adv_lines[i + 1]:
                                        i += 1
                                        iso, d1, d2, d3, d4 = self.parse_isotachs(
                                            adv_lines[i])
                                        forecasts[-1].set_isotach(
                                            iso, d1, d2, d3, d4)
                            i += 1

                        if self.__use_aws:
                            self.write_atcf(self.__dblocation + "/" + fn, basin_str, storm_name, storm_str, forecasts)
                            self.__s3file.upload_file(self.__dblocation + "/" + fn, filepath)
                            start_date, end_date, duration = self.get_nhc_start_end_date(
                                self.__dblocation + "/" + fn, True)
                        else:
                            self.write_atcf(filepath, basin_str, storm_name, storm_str,
                                            forecasts)
                            start_date, end_date, duration = self.get_nhc_start_end_date(
                                filepath, True)

                        nhc_metadata = {
                            "year": year_str,
                            "basin": basin_str,
                            "storm": storm_str,
                            "advisory": adv_number,
                            'advisory_start': start_date,
                            'advisory_end': end_date,
                            'advisory_duration_hr': duration
                        }
                        self.__database.add(nhc_metadata, "nhc_fcst", filepath)

                        # Increment the counter
                        n += 1
            return n
        except KeyboardInterrupt:
            raise
        except:
            print("[ERROR]: An error occured reading the NHC RSS feed")
            return n

    @staticmethod
    def print_forecast_data(year, basin, storm_name, storm_number,
                            advisory_number, forecast_data):
        print("Basin: ", basin2string(basin), ", Year:", year, ", Storm: ",
              storm_name, "(", storm_number, "), Advisory: " + advisory_number)
        for f in forecast_data:
            f.print()
        print("")

    @staticmethod
    def write_atcf(filepath, basin, storm_name, storm_number, forecast_data):
        import os
        with open(filepath, 'w') as f:
            for d in forecast_data:
                line = "{:2s},{:3s},{:10s},".format(
                    basin,
                    storm_number.strip().rjust(3),
                    forecast_data[0].time().strftime(" %Y%m%d%H"))
                line = line + " 00, OFCL,{:4.0f},".format(d.forecast_hour())

                x, y = d.storm_center()
                x = int(round(x * 10))
                y = int(round(y * 10))

                if x < 0:
                    x = "{:5d}".format(abs(x)) + "W"
                else:
                    x = "{:5d}".format(x) + "E"

                if y < 0:
                    y = "{:4d}".format(abs(y)) + "S"
                else:
                    y = "{:4d}".format(y) + "N"

                if d.max_wind() < 34:
                    windcode = "TD"
                elif d.max_wind() < 63:
                    windcode = "TS"
                else:
                    windcode = "HU"

                line = line + "{:5s},{:6s},{:4.0f},{:5.0f},{:3s},".format(
                    y.strip().rjust(5),
                    x.strip().rjust(6), d.max_wind(), d.pressure(),
                    windcode.rjust(3))

                if d.heading() > -900:
                    heading = d.heading()
                else:
                    heading = 0

                if d.forward_speed() > -900:
                    fspd = d.forward_speed()
                else:
                    fspd = 0

                if len(d.isotach_levels()) > 0:
                    for it in sorted(d.isotach_levels()):
                        iso = d.isotach(it)
                        itline = line + "{:4d}, NEQ,{:5d},{:5d},{:5d},{:5d},".format(
                            it, iso.distance(0), iso.distance(1), iso.distance(2),
                            iso.distance(3))
                        itline = itline + " 1013,    0,   0,{:4.0f},   0,   0,    ,METG,{:4d},{:4d}," \
                                          "{:11s},  ,  0, NEQ,    0,    0,    0,    0,            ,    ,".format(
                            d.max_gust(), heading, fspd, storm_name.upper().rjust(11))
                        f.write(itline)
                        f.write(os.linesep)
                else:
                    itline = line + "{:4d}, NEQ,{:5d},{:5d},{:5d},{:5d},".format(
                        34, 0, 0, 0, 0)
                    itline = itline + " 1013,    0,   0,{:4.0f},   0,   0,    ,METG,{:4d},{:4d}," \
                                      "{:11s},  ,  0, NEQ,    0,    0,    0,    0,            ,    ,".format(
                        d.max_gust(), heading, fspd, storm_name.upper().rjust(11))
                    f.write(itline)
                    f.write(os.linesep)

        return

    @staticmethod
    def get_storm_center(x, y):
        if "W" in x:
            x = -float(x[:-1])
        else:
            x = float(x[:-1])
        if "S" in y:
            y = -float(y[:-1])
        else:
            y = float(y[:-1])
        return x, y

    @staticmethod
    def get_rss_time(time_str):
        from datetime import datetime
        now = datetime.utcnow()
        day = int(time_str[0:2])
        hr = int(time_str[3:5])
        d = datetime(now.year, now.month, day, hr, 0, 0)
        if d < datetime.now():
            return datetime(now.year, now.month + 1, day, hr, 0, 0)
        else:
            return d

    @staticmethod
    def parse_isotachs(line):
        data = line.replace(".", " ").split()
        iso = int(data[0])
        d1 = int(data[2][:-2])
        d2 = int(data[3][:-2])
        d3 = int(data[4][:-2])
        d4 = int(data[5][:-2])
        return iso, d1, d2, d3, d4

    def download_forecast_ftp(self):
        from ftplib import FTP
        import os.path

        try:
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
                    site = self.generate_storm_forecast_homepage_url(
                        year, basin, storm)
                    advlist = self.get_advisories(site)
                    if advlist:
                        latest_advisory = advlist[-1]
                        filepath = self.__downloadlocation + "_fcst/nhc_fcst_" + year + "_" + basin + \
                                   "_" + storm + "_" + "{:03d}".format(latest_advisory) + ".fcst"
                        if not os.path.exists(filepath):
                            print("    Downloading NHC forecast for Basin: " +
                                  basin2string(basin) + ", Year: " + str(year) +
                                  ", Storm: " + str(storm) + ", Advisory: " +
                                  str(latest_advisory),
                                  flush=True)
                            ftp.retrbinary("RETR " + f, open(filepath, 'wb').write)
                            start_date, end_date, duration = self.get_nhc_start_end_date(
                                filepath, True)
                            data = {
                                "year": int(year),
                                "basin": basin,
                                "storm": int(storm),
                                "advisory": latest_advisory,
                                'advisory_start': start_date,
                                'advisory_end': end_date,
                                'advisory_duration_hr': duration
                            }
                            self.__database.add(data, "nhc_fcst", filepath)
                            n += 1
            return n
        except KeyboardInterrupt:
            raise
        except:
            print("[ERROR]: An error occured connecting to the NHC ftp site", flush=True)
            return 0

    def download_hindcast(self):
        from ftplib import FTP
        import os.path

        print("[INFO]: Connecting to NHC FTP site")

        # Anonymous FTP login
        try:
            ftp = FTP('ftp.nhc.noaa.gov')
            ftp.login()
            ftp.cwd('atcf/btk')
            filelist = ftp.nlst("*.dat")
            print("[INFO]: NHC FTP connection successful")

            n = 0

            # Iterate through files and find the associated advisory
            for f in filelist:
                year = f[5:9]
                if int(year) == self.__year:
                    basin = f[1:3]
                    storm = f[3:5]
                    filepath = self.__downloadlocation + "_btk/nhc_btk_" + year + "_" + basin + "_" + storm + ".btk"

                    if os.path.exists(filepath):
                        md5_original = self.compute_checksum(filepath)
                    else:
                        md5_original = 0

                    try:
                        ftp.retrbinary("RETR " + f, open(filepath, 'wb').write)
                    except KeyboardInterrupt:
                        raise
                    except:
                        continue

                    start_date, end_date, duration = self.get_nhc_start_end_date(
                        filepath, False)
                    md5_updated = self.compute_checksum(filepath)
                    if not md5_original == md5_updated:
                        if md5_original == 0:
                            print("    Downloaded NHC best track for Basin: " +
                                  basin2string(basin) + ", Year: " + str(year) +
                                  ", Storm: " + str(storm),
                                  flush=True)
                        else:
                            print(
                                "    Downloaded updated NHC best track for Basin: "
                                + basin2string(basin) + ", Year: " + str(year) +
                                ", Storm: " + str(storm),
                                flush=True)
                        data = {
                            "year": int(year),
                            "basin": basin,
                            "storm": storm,
                            'advisory_start': start_date,
                            'advisory_end': end_date,
                            'advisory_duration_hr': duration
                        }
                        self.__database.add(data, "nhc_btk", filepath)
                        n += 1
            return n
        except KeyboardInterrupt:
            raise
        except:
            print("[ERROR]: An error occured connecting to the NHC ftp site", flush=True)
            return 0

    @staticmethod
    def generate_storm_forecast_homepage_url(year, basin, storm):
        return "https://www.nhc.noaa.gov/archive/" + year + "/" + basin + storm

    @staticmethod
    def compute_checksum(path):
        import hashlib
        with open(path, "rb") as file:
            data = file.read()
            return hashlib.md5(data).hexdigest()

    @staticmethod
    def get_advisories(url):
        import requests
        from bs4 import BeautifulSoup
        try:
            r = requests.get(url, timeout=30)
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
                except KeyboardInterrupt:
                    raise
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
                lastline = l
                if line == 0:
                    firstline = l
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
    basin_abbrev = basin_abbrev.lower()
    if basin_abbrev == "ep":
        return "Eastern Pacific"
    elif basin_abbrev == "al":
        return "Atlantic"
    elif basin_abbrev == "cp":
        return "Central Pacific"
    return basin_abbrev
