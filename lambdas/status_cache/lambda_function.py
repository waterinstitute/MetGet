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
class Database:
    def __init__(self):
        import sys
        import os
        import pymysql
        self.__dbhost = os.environ["DBSERVER"]
        self.__dbpassword = os.environ["DBPASS"]
        self.__dbusername = os.environ["DBUSER"]
        self.__dbname = os.environ["DBNAME"]

        try:
            self.__db = pymysql.connect(host=self.__dbhost, user=self.__dbusername,
                                        passwd=self.__dbpassword, db=self.__dbname, connect_timeout=5)
            self.__cursor = self.__db.cursor()
        except:
            print("[ERROR]: Could not connect to MySQL database")
            sys.exit(1)

    def cursor(self):
        return self.__cursor

    def generate_status(self):
        jsondata = {'metget': {}}
        jsondata['metget']['nam-ncep'] = self.generate_status_nam()
        jsondata['metget']['gfs-ncep'] = self.generate_status_gfs()
        jsondata['metget']['hwrf'] = self.generate_hwrf_status()
        return jsondata

    @staticmethod
    def generate_record_period():
        from datetime import datetime
        from datetime import timedelta
        now = datetime.now()
        prev_month = now - timedelta(days=31)
        prev_month = datetime(prev_month.year, prev_month.month, prev_month.day, 0, 0, 0)
        return str(prev_month)

    def generate_status_generic(self, table, desired_len):
        from datetime import datetime

        search_period = Database.generate_record_period()

        self.cursor().execute(
            "SELECT DISTINCT FORECASTCYCLE FROM " + table + " WHERE FORECASTCYCLE > '" + search_period + "' ORDER BY FORECASTCYCLE")

        rows = self.cursor().fetchall()
        if len(rows) < 1:
            return {
                "min_forecast_date": None,
                "max_forecast_date": None,
                "first_available_cycle": None,
                "last_available_cycle": None,
                "last_available_length": None,
                "latest_complete_forecast": None,
                "latest_complete_forecast_start": None,
                "latest_complete_forecast_end": None,
                "latest_complete_forecast_length": None
            }

        cyc_min = rows[0][0]
        if len(rows) > 1:
            cyc_max = rows[-1][0]
        else:
            cyc_max = cyc_min

        latest_complete = None
        latest_start = None
        latest_end = None
        latest_length = None
        last_available_length = None
        cycle_list = []
        for r in reversed(rows):
            sql = "SELECT MIN(FORECASTTIME) AS FIRST, MAX(FORECASTTIME) AS LAST FROM " + table + " WHERE FORECASTCYCLE = '" + datetime.strftime(
                r[0], "%Y-%m-%d %H:%M:%S") + "'"
            self.cursor().execute(sql)
            rr = self.cursor().fetchall()
            start = rr[0][0]
            end = rr[0][1]
            avail_len = (end - start).total_seconds() / 3600

            if cyc_max == r[0]:
                last_available_length = avail_len

            if avail_len >= desired_len:
                cycle_list.append(r[0].strftime("%Y-%m-%d %H:%M:%S"))
                if latest_complete == None:
                    latest_complete = r[0]
                    latest_start = start.strftime("%Y-%m-%d %H:%M:%S")
                    latest_end = end.strftime("%Y-%m-%d %H:%M:%S")
                    latest_length = avail_len

        sql = "SELECT MIN(FORECASTTIME) AS FIRST, MAX(FORECASTTIME) AS LAST FROM " + table
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        fcst_min = rows[0][0]
        fcst_max = rows[0][1]

        return {
            "min_forecast_date": fcst_min.strftime("%Y-%m-%d %H:%M:%S"),
            "max_forecast_date": fcst_max.strftime("%Y-%m-%d %H:%M:%S"),
            "first_available_cycle": cyc_min.strftime("%Y-%m-%d %H:%M:%S"),
            "last_available_cycle": cyc_max.strftime("%Y-%m-%d %H:%M:%S"),
            "last_available_length": last_available_length,
            "latest_complete_forecast": latest_complete.strftime("%Y-%m-%d %H:%M:%S"),
            "latest_complete_forecast_start": latest_start,
            "latest_complete_forecast_end": latest_end,
            "latest_complete_forecast_length": latest_length,
            "cycle_list": cycle_list
        }

    def generate_status_nam(self):
        return self.generate_status_generic("nam_ncep", 84)

    def generate_status_gfs(self):
        return self.generate_status_generic("gfs_ncep", 384)

    def generate_hwrf_status(self):
        """
        Generates the json status object from the database for the available HWRF data
        :return: json status object
        """
        from datetime import datetime

        search_period = Database.generate_record_period()

        # Use SQL to generate a distinct list of storms and then
        # iterate over them to determine the available forecast data
        stormlist = []
        self.cursor().execute("SELECT DISTINCT stormname from hwrf WHERE FORECASTCYCLE > '" + search_period + "'")
        rows = self.cursor().fetchall()
        for row in rows:
            stormlist.append({"storm": row[0]})

        hwrf_stat = []

        # For each storm, determine the availability of data
        for s in stormlist:
            sql = "SELECT FORECASTTIME FROM hwrf WHERE stormname = '" + s[
                "storm"] + "' ORDER BY FORECASTTIME"
            self.cursor().execute(sql)
            rows = self.cursor().fetchall()
            fcst_min = rows[0][0]
            fcst_max = rows[-1][0]
            sql = "SELECT DISTINCT FORECASTCYCLE FROM hwrf WHERE stormname = '" + s[
                "storm"] + "' ORDER BY FORECASTCYCLE"
            self.cursor().execute(sql)
            rows = self.cursor().fetchall()
            cyc_min = rows[0][0]
            cyc_max = rows[-1][0]

            latest_complete = None
            latest_start = None
            latest_end = None
            latest_length = None
            time_since_forecast = 0
            cycle_list = []

            # Backwards loop to see the most recent complete forecast cycle
            for f in reversed(rows):
                sql = "SELECT MIN(FORECASTTIME) AS FIRST, MAX(FORECASTTIME) AS LAST FROM hwrf WHERE stormname = '" + s[
                    "storm"] + "' AND FORECASTCYCLE = '" + datetime.strftime(f[0],
                                                                             "%Y-%m-%d %H:%M:%S") + "' ORDER BY FORECASTTIME"
                self.cursor().execute(sql)
                r = self.cursor().fetchall()
                start = r[0][0]
                end = r[0][1]
                avail_len = (end - start).total_seconds() / 3600
                if avail_len >= 126:
                    cycle_list.append(f[0].strftime("%Y-%m-%d %H:%M:%S"), )
                    latest_start = start.strftime("%Y-%m-%d %H:%M:%S")
                    latest_end = end.strftime("%Y-%m-%d %H:%M:%S")
                    latest_length = avail_len
                    latest_complete = f[0]
                    time_since_forecast = (datetime.now() - f[0]).total_seconds() / 86400
                    continue

            # Assemble a storm object. We're only going to write data available in the last 10 days
            if time_since_forecast < 10:
                hwrf_stat.append({
                    "storm":
                        s["storm"],
                    "min_forecast_date":
                        date_or_null(fcst_min),
                    "max_forecast_date":
                        date_or_null(fcst_max),
                    "first_available_cycle":
                        date_or_null(cyc_min),
                    "last_available_cycle":
                        date_or_null(cyc_max),
                    "latest_complete_forecast":
                        date_or_null(latest_complete),
                    "latest_complete_forecast_start":
                        latest_start,
                    "latest_complete_forecast_end":
                        latest_end,
                    "latest_complete_forecast_length":
                        latest_length,
                    "cycle_list": cycle_list
                })

        return hwrf_stat


def date_or_null(date):
    from datetime import datetime
    if not isinstance(date, datetime):
        return None
    else:
        return date.strftime("%Y-%m-%d %H:%M:%S")


def write_to_cache(json_data):
    import pymysql
    import os
    import sys
    import json
    dbhost = os.environ["DBSERVER"]
    dbpassword = os.environ["DBPASS"]
    dbusername = os.environ["DBUSER"]
    dbname = "lambda_cache"

    try:
        db = pymysql.connect(dbhost, user=dbusername, passwd=dbpassword, db=dbname, connect_timeout=5)
        cursor = db.cursor()
    except:
        print("[ERROR]: Could not connect to MySQL database")
        sys.exit(1)

    sql_insert = "INSERT INTO status (json) VALUES('" + json.dumps(json_data) + "')"

    cursor.execute("DELETE from status")
    cursor.execute(sql_insert)
    db.commit()


def lambda_handler(event, context):
    db = Database()
    s = db.generate_status()
    write_to_cache(s)
    return {"statusCode": 200}
