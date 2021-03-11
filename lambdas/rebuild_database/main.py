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
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
#
def rebuild_database():
    import boto3
    from datetime import datetime, timedelta
    from metdb import Metdb

    db = Metdb()

    session = boto3.session.Session(profile_name="unc")
    client = session.client("s3")
    bucket = "metget-data"

    has_next = True
    next_marker = ""
    while has_next:
        if next_marker == "":
            response = client.list_objects_v2(Bucket=bucket)
        else:
            response = client.list_objects_v2(Bucket=bucket, ContinuationToken=next_marker)

        has_next = response["IsTruncated"]
        if has_next:
            next_marker = response["NextContinuationToken"]

        for file in response["Contents"]:
            split_path = file["Key"].split("/")
            datatype = split_path[0]
            pair = {}
            if datatype == "gfs_ncep":
                cycle_year = int(split_path[1])
                cycle_month = int(split_path[2])
                cycle_day = int(split_path[3])
                fn = split_path[4].split(".")
                cycle_hour = int(fn[1][1:3])
                forecast_hour = int(fn[4][1:])
                cycle_date = datetime(cycle_year, cycle_month, cycle_day, cycle_hour)
                forecast_date = cycle_date + timedelta(hours=forecast_hour)
                pair = {"cycledate": cycle_date, "forecastdate": forecast_date, "grb": "n/a"}
            elif datatype == "nam_ncep":
                cycle_year = int(split_path[1])
                cycle_month = int(split_path[2])
                cycle_day = int(split_path[3])
                fn = split_path[4].split(".")
                cycle_hour = int(fn[1][1:3])
                forecast_hour = int(fn[2][6:])
                cycle_date = datetime(cycle_year, cycle_month, cycle_day, cycle_hour)
                forecast_date = cycle_date + timedelta(hours=forecast_hour)
                pair = {"cycledate": cycle_date, "forecastdate": forecast_date, "grb": "n/a"}
            elif datatype == "hwrf":
                cycle_year = int(split_path[1])
                cycle_month = int(split_path[2])
                cycle_day = int(split_path[3])
                fn = split_path[4].split(".")
                storm_name = fn[0]
                cycle_hour = int(fn[1][8:])
                forecast_hour = int(fn[5][1:])
                cycle_date = datetime(cycle_year, cycle_month, cycle_day, cycle_hour)
                forecast_date = cycle_date + timedelta(hours=forecast_hour)
                pair = {"cycledate": cycle_date, "forecastdate": forecast_date, "grb": "n/a", "name": storm_name}

            db.add(pair, datatype, file["Key"])

    db.disconnect()


if __name__ == '__main__':
    rebuild_database()
