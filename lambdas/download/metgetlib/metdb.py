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


class Metdb:
    def __init__(self):
        """
        Initializer for the metdb class. The Metdb class will
        generate a database of files and store the indexing in an
        sqlite3 database
        """
        import os
        self.__dbhost = os.environ["DBSERVER"]
        self.__dbpassword = os.environ["DBPASS"]
        self.__dbusername = os.environ["DBUSER"]
        self.__dbname = os.environ["DBNAME"]

        self.__initdatabase()

    def connect(self):
        import sys
        import pymysql
        try:
            return pymysql.connect(host=self.__dbhost, user=self.__dbusername,
                                   passwd=self.__dbpassword, db=self.__dbname, connect_timeout=5)
        except:
            print("[ERROR]: Could not connect to MySQL database")
            sys.exit(1)

    def __initdatabase(self):
        """
        Initializes the database with the appropriate tables
        :return:
        """
        db = self.connect()
        cur = db.cursor()

        cur.execute(
            'CREATE TABLE IF NOT EXISTS gfs_ncep(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME NOT NULL, forecasttime DATETIME NOT NULL, '
            'filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        cur.execute(
            'CREATE TABLE IF NOT EXISTS gfs_fcst(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME '
            'NOT NULL, forecasttime DATETIME NOT NULL, filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, '
            'accessed DATETIME NOT NULL);')
        # db.execute('CREATE TABLE IF NOT EXISTS nam_anl(id INTEGER PRIMARY KEY '
        #            'AUTOINCREMENT, forecastcycle DATETIME '
        #            'NOT NULL, date DATETIME NOT NULL, path STRING NOT NULL, url STRING NOT NULL, '
        #            'accessed DATETIME NOT NULL);')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS nam_fcst(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME '
            'NOT NULL, forecasttime DATETIME NOT NULL, filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, '
            'accessed DATETIME NOT NULL);')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS hwrf(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, stormname VARCHAR(256) NOT NULL, forecastcycle DATETIME '
            'NOT NULL, forecasttime DATETIME NOT NULL, filepath VARCHAR(256) NOT NULL, '
            'url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS nam_ncep(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME NOT NULL, forecasttime DATETIME NOT NULL, '
            'filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        cur.execute(
            'CREATE TABLE IF NOT EXISTS nhc_btk(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, storm_year INTEGER NOT NULL, basin VARCHAR(256) NOT NULL, storm INTEGER NOT NULL, '
            'advisory_start DATETIME NOT NULL, advisory_end DATETIME NOT NULL, '
            'advisory_duration_hr INT NOT NULL, filepath VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        cur.execute(
            'CREATE TABLE IF NOT EXISTS nhc_fcst(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, storm_year INTEGER NOT NULL, basin VARCHAR(256) NOT NULL, storm INTEGER NOT NULL, '
            'advisory VARCHAR(256) NOT NULL, advisory_start DATETIME NOT NULL, advisory_end DATETIME NOT NULL, '
            'advisory_duration_hr INT NOT NULL, filepath VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        db.close()

    def add(self, pair, datatype, filepath):
        """
        Adds a file listing to the database
        :param pair: dict containing cycledate and forecastdate
        :param datatype: The table that this file will be added to (i.e. gfsfcst)
        :param filepath: Relative file location
        :return:
        """
        db = self.connect()
        if datatype == "hwrf":
            cdate = str(pair["cycledate"])
            fdate = str(pair["forecastdate"])
            url = pair["grb"]
            name = pair["name"]
            sqlhas = "SELECT Count(*) FROM " + datatype + " WHERE FORECASTCYCLE = '" + \
                     cdate + "' AND FORECASTTIME = '" + fdate + "' AND STORMNAME = '" + \
                     name + "' AND FILEPATH = '" + filepath + "';"
            sqlinsert = "INSERT INTO " + datatype + " (FORECASTCYCLE,FORECASTTIME,STORMNAME,FILEPATH,URL,ACCESSED) VALUES('" + cdate + \
                        "','" + fdate + "','" + name + "','" + filepath + "','" + url + "',now());"
            sqlupdate = ""
        elif datatype == "nhc_fcst":
            year = pair["year"]
            storm = pair["storm"]
            advisory = pair["advisory"]
            basin = pair["basin"]
            start = str(pair["advisory_start"])
            end = str(pair["advisory_end"])
            duration = str(pair["advisory_duration_hr"])
            sqlhas = "SELECT Count(*) FROM " + datatype + " WHERE storm_year = " + str(year) + " AND ADVISORY = " + \
                     advisory + " AND BASIN = '" + basin + "' AND STORM = " + str(storm) + ";"
            sqlinsert = "INSERT INTO " + datatype + " (STORM_YEAR,BASIN,STORM,ADVISORY,ADVISORY_START,ADVISORY_END," \
                                                    "ADVISORY_DURATION_HR,FILEPATH,ACCESSED) VALUES(" + str(year) + \
                        ",'" + basin + "'," + str(storm) + "," + advisory + ", '" + start + \
                        "', '" + end + "', " + duration + ",'" + filepath + "', now());"
            sqlupdate = ""
        elif datatype == "nhc_btk":
            year = pair["year"]
            storm = pair["storm"]
            basin = pair["basin"]
            start = str(pair["advisory_start"])
            end = str(pair["advisory_end"])
            duration = str(pair["advisory_duration_hr"])
            sqlhas = "SELECT Count(*) FROM " + datatype + " WHERE storm_year = " + str(
                year) + " AND BASIN = '" + basin + "' AND STORM = " + str(
                storm) + ";"
            sqlinsert = "INSERT INTO " + datatype + " (STORM_YEAR,BASIN,STORM,ADVISORY_START,ADVISORY_END," \
                                                    "ADVISORY_DURATION_HR,FILEPATH,ACCESSED) VALUES(" + str(year) + \
                        ",'" + basin + "'," + str(storm) + ", '" + start + \
                        "', '" + end + "', " + duration + ",'" + filepath + "', now());"
            sqlupdate = "UPDATE " + datatype + " SET ACCESSED = now() WHERE storm_year = " + str(
                year) + " AND BASIN = '" + basin + "' AND STORM = " + str(
                storm) + ";"
        else:
            cdate = str(pair["cycledate"])
            fdate = str(pair["forecastdate"])
            url = pair["grb"]
            sqlhas = "SELECT Count(*) FROM " + datatype + \
                     " WHERE FORECASTCYCLE = '" + \
                     cdate + "' AND FORECASTTIME = '" + \
                     fdate + "' AND FILEPATH = '" + filepath + "';"
            sqlinsert = "INSERT INTO " + datatype + \
                        " (FORECASTCYCLE,FORECASTTIME,FILEPATH,URL,ACCESSED) VALUES('" + \
                        cdate + "','" + fdate + "','" + filepath + "','" + \
                        url + "',now());"
            sqlupdate = ""

        cur = db.cursor()
        cur.execute(sqlhas)
        nrows = cur.fetchone()[0]
        if nrows == 0:
            cur.execute(sqlinsert)
        elif nrows > 0 and datatype == "nhc_btk":
            cur.execute(sqlupdate)

        db.commit()
        db.close()

    def status(self, jsonfile):
        """
        Writes a json file which contains the latest state of the meteorological database
        :param jsonfile: output json file
        """
        import json
        import socket
        from datetime import datetime

        jsondata = {'metget': {}}
        jsondata['metget']['hwrf'] = self.hwrf_status()
        jsondata['metget']['gfs-ncep'] = self.generic_status("gfs_ncep", 384)
        jsondata['metget']['nam-ncep'] = self.generic_status("nam_ncep", 84)
        jsondata['metget']['nhc'] = {}
        jsondata['metget']['nhc']["forecast"], jsondata['metget']['nhc'][
            "best_track"] = self.nhc_status()
        jsondata['metget']['state'] = {
            'last_fetch': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'host': socket.gethostname()
        }

        with open(jsonfile, 'w') as statfile:
            json.dump(jsondata, statfile, indent=1)

    def generic_status(self, table, desired_len):
        """
        Generates json status object from the avaialable NCEP-GFS data
        :return: json status object
        """
        from datetime import datetime
        db = self.connect()

        sql = "SELECT DISTINCT FORECASTCYCLE FROM " + table + " ORDER BY FORECASTCYCLE"
        rows = db.execute(sql).fetchall()

        if len(rows) < 1:
            return {
                "min_forecast_date": None,
                "max_forecast_date": None,
                "first_available_cycle": None,
                "last_available_cycle": None,
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
        cycle_list = []
        for r in reversed(rows):
            sql = "SELECT MIN(DATE) AS FIRST, MAX(DATE) AS LAST FROM " + table + " WHERE FORECASTCYCLE = datetime('" + \
                  r[0] + "')"
            rr = db.execute(sql).fetchall()
            start = datetime.strptime(rr[0][0], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(rr[0][1], "%Y-%m-%d %H:%M:%S")
            avail_len = (end - start).total_seconds() / 3600
            if avail_len >= desired_len:
                latest_complete = r[0]
                cycle_list.append(r[0])
                latest_start = start.strftime("%Y-%m-%d %H:%M:%S")
                latest_end = end.strftime("%Y-%m-%d %H:%M:%S")
                latest_length = avail_len
                break

        sql = "SELECT MIN(DATE) AS FIRST, MAX(DATE) AS LAST FROM " + table
        rows = db.execute(sql).fetchall()
        fcst_min = rows[0][0]
        fcst_max = rows[0][1]

        return {
            "min_forecast_date": fcst_min,
            "max_forecast_date": fcst_max,
            "first_available_cycle": cyc_min,
            "last_available_cycle": cyc_max,
            "latest_complete_forecast": latest_complete,
            "latest_complete_forecast_start": latest_start,
            "latest_complete_forecast_end": latest_end,
            "latest_complete_forecast_length": latest_length,
            "cycle_list": cycle_list
        }

    def hwrf_status(self):
        """
        Generates the json status object from the database for the available HWRF data
        :return: json status object
        """
        import sqlite3
        from datetime import datetime
        db = sqlite3.connect(self.__db)

        # Use SQL to generate a distinct list of storms and then
        # iterate over them to determine the available forecast data
        sql = "SELECT DISTINCT stormname FROM hwrf"
        stormlist = []
        rows = db.execute(sql).fetchall()
        for row in rows:
            stormlist.append({"storm": row[0]})

        hwrf_stat = []

        # For each storm, determine the availability of data
        for s in stormlist:
            sql = "SELECT DATE FROM hwrf WHERE stormname = '" + s[
                "storm"] + "' ORDER BY DATE"
            rows = db.execute(sql).fetchall()
            fcst_min = rows[0][0]
            fcst_max = rows[-1][0]
            sql = "SELECT DISTINCT FORECASTCYCLE FROM hwrf WHERE stormname = '" + s[
                "storm"] + "' ORDER BY FORECASTCYCLE"
            rows = db.execute(sql).fetchall()
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
                sql = "SELECT MIN(DATE) AS FIRST, MAX(DATE) AS LAST FROM hwrf WHERE stormname = '" + s[
                    "storm"] + "' AND FORECASTCYCLE = datetime('" + f[
                          0] + "') ORDER BY DATE"
                r = db.execute(sql).fetchall()
                start = datetime.strptime(r[0][0], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(r[0][1], "%Y-%m-%d %H:%M:%S")
                avail_len = (end - start).total_seconds() / 3600
                if avail_len >= 126:
                    cycle_list.append(f[0])
                    latest_start = start.strftime("%Y-%m-%d %H:%M:%S")
                    latest_end = end.strftime("%Y-%m-%d %H:%M:%S")
                    latest_length = avail_len
                    latest_complete = f[0]
                    time_since_forecast = datetime.now() - datetime.strptime(
                        f[0], "%Y-%m-%d %H:%M:%S")
                    time_since_forecast = time_since_forecast.total_seconds(
                    ) / 86400
                    break

            # Assemble a storm object. We're only going to write data available in the last 10 days
            if time_since_forecast < 10:
                hwrf_stat.append({
                    "storm":
                        s["storm"],
                    "min_forecast_date":
                        fcst_min,
                    "max_forecast_date":
                        fcst_max,
                    "first_available_cycle":
                        cyc_min,
                    "last_available_cycle":
                        cyc_max,
                    "latest_complete_forecast":
                        latest_complete,
                    "latest_complete_forecast_start":
                        latest_start,
                    "latest_complete_forecast_end":
                        latest_end,
                    "latest_complete_forecast_length":
                        latest_length,
                    "cycle_list": cycle_list
                })

        return hwrf_stat

    def nhc_status(self):
        import sqlite3
        from .nhcdownloader import basin2string
        db = sqlite3.connect(self.__db)

        nhc_btk_stat = []
        nhc_fcst_stat = []
        latest_forecast_advisory = 0

        sql = "SELECT DISTINCT year, basin, storm FROM nhc_fcst ORDER BY year, basin, storm, advisory;"
        crsr = db.execute(sql)
        for f in crsr:
            forecast_advisory_list = []
            yr = f[0]
            bs = f[1]
            st = f[2]
            sql = "SELECT advisory, advisory_start, advisory_end, advisory_duration_hr FROM nhc_fcst WHERE year = " + str(
                yr) + " and basin = '" + bs + "' and storm = " + str(
                st) + " ORDER BY advisory;"
            crsr2 = db.execute(sql)
            for ff in crsr2:
                adv_data = {
                    "advisory": ff[0],
                    "start": ff[1],
                    "end": ff[2],
                    "duration": ff[3]
                }
                forecast_advisory_list.append(adv_data)
                latest_forecast_advisory = ff[0]

            nhc_fcst_stat.append({
                "year":
                    yr,
                "basin_abbrev":
                    bs,
                "basin_string":
                    basin2string(bs),
                "storm":
                    st,
                "latest_forecast_advisory":
                    latest_forecast_advisory,
                "available_forecast_advisories":
                    forecast_advisory_list
            })

        sql = "SELECT DISTINCT year, basin, storm, advisory_start, advisory_end, advisory_duration_hr, accessed " \
              "FROM nhc_btk ORDER BY year, basin, storm;"
        crsr = db.execute(sql)
        for f in crsr:
            nhc_btk_stat.append({
                "year": f[0],
                "basin": f[1],
                "basin_string": basin2string(f[1]),
                "storm": f[2],
                "start": f[3],
                "end": f[4],
                "duration": f[5],
                "last_update": f[6]
            })

        return nhc_fcst_stat, nhc_btk_stat
