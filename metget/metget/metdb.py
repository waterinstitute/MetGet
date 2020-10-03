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
    def __init__(self, location):
        """
        Initializer for the metdb class. The Metdb class will
        generate a database of files and store the indexing in an
        sqlite3 database
        :param location:
        """
        self.__location = location
        self.__db = self.__location + "/metget.db"
        self.__initfolderstructure()
        self.__initdatabase()

    def __initfolderstructure(self):
        """
        Generates the directory structure used in the top level of the database
        :return:
        """
        import os.path
        if not os.path.exists(self.__location):
            os.mkdir(self.__location)
        if not os.path.exists(self.__location + "/gfs_ncep"):
            os.mkdir(self.__location + "/gfs_ncep")
        if not os.path.exists(self.__location + "/gfs_fcst"):
            os.mkdir(self.__location + "/gfs_fcst")
        if not os.path.exists(self.__location + "/gfs_anl"):
            os.mkdir(self.__location + "/gfs_anl")
        if not os.path.exists(self.__location + "/nam_anl"):
            os.mkdir(self.__location + "/nam_anl")
        if not os.path.exists(self.__location + "/nam_fcst"):
            os.mkdir(self.__location + "/nam_fcst")
        if not os.path.exists(self.__location + "/nam_ncep"):
            os.mkdir(self.__location + "/nam_ncep")
        if not os.path.exists(self.__location + "/hwrf"):
            os.mkdir(self.__location + "/hwrf")

    def __initdatabase(self):
        """
        Initializes the database with the appropriate tables
        :return:
        """
        import sqlite3
        db = sqlite3.connect(self.__db)
        db.execute('CREATE TABLE IF NOT EXISTS gfs_ncep(id INTEGER PRIMARY KEY '
                   'AUTOINCREMENT, forecastcycle DATETIME NOT NULL, date DATETIME NOT NULL, '
                   'path STRING NOT NULL, url STRING NOT NULL, accessed DATETIME NOT NULL);')
        db.execute('CREATE TABLE IF NOT EXISTS gfs_fcst(id INTEGER PRIMARY KEY '
                   'AUTOINCREMENT, forecastcycle DATETIME '
                   'NOT NULL, date DATETIME NOT NULL, path STRING NOT NULL, url STRING NOT NULL, '
                   'accessed DATETIME NOT NULL);')
        # db.execute('CREATE TABLE IF NOT EXISTS nam_anl(id INTEGER PRIMARY KEY '
        #            'AUTOINCREMENT, forecastcycle DATETIME '
        #            'NOT NULL, date DATETIME NOT NULL, path STRING NOT NULL, url STRING NOT NULL, '
        #            'accessed DATETIME NOT NULL);')
        db.execute('CREATE TABLE IF NOT EXISTS nam_fcst(id INTEGER PRIMARY KEY '
                   'AUTOINCREMENT, forecastcycle DATETIME '
                   'NOT NULL, date DATETIME NOT NULL, path STRING NOT NULL, url STRING NOT NULL, '
                   'accessed DATETIME NOT NULL);')
        db.execute('CREATE TABLE IF NOT EXISTS hwrf(id INTEGER PRIMARY KEY '
                   'AUTOINCREMENT, stormname STRING NOT NULL, forecastcycle DATETIME '
                   'NOT NULL, date DATETIME NOT NULL, path STRING NOT NULL, '
                   'url STRING NOT NULL, accessed DATETIME NOT NULL);')
        db.execute('CREATE TABLE IF NOT EXISTS nam_ncep(id INTEGER PRIMARY KEY '
                   'AUTOINCREMENT, forecastcycle DATETIME NOT NULL, date DATETIME NOT NULL, '
                   'path STRING NOT NULL, url STRING NOT NULL, accessed DATETIME NOT NULL);')
        db.close()

    def add(self, pair, datatype, filepath):
        """
        Adds a file listing to the database
        :param pair: dict containing cycledate and forecastdate
        :param datatype: The table that this file will be added to (i.e. gfsfcst)
        :param filepath: Relative file location
        :return:
        """
        import sqlite3
        db = sqlite3.connect(self.__db)
        cdate = str(pair["cycledate"])
        fdate = str(pair["forecastdate"])
        url = pair["grb"]
        if datatype == "hwrf":
            name = pair["name"]
            sqlhas = "SELECT Count(*) FROM " + datatype + \
                     " WHERE FORECASTCYCLE = datetime('" + \
                     cdate + "') AND DATE = datetime('" + \
                     fdate + "') AND STORMNAME = '" + name + \
                     "' AND PATH = '" + filepath + "';"
            sqlinsert = "INSERT INTO " + datatype + \
                        " (FORECASTCYCLE,DATE,STORMNAME,PATH,URL,ACCESSED) VALUES(datetime('" + \
                        cdate + "'),datetime('" + fdate + "'),'" + name + "','" + filepath + "','" + \
                        url + "',datetime('now'));"
        else:
            sqlhas = "SELECT Count(*) FROM " + datatype + \
                     " WHERE FORECASTCYCLE = datetime('" + \
                     cdate + "') AND DATE = datetime('" + \
                     fdate + "') AND PATH = '" + filepath + "';"
            sqlinsert = "INSERT INTO " + datatype + \
                        " (FORECASTCYCLE,DATE,PATH,URL,ACCESSED) VALUES(datetime('" + \
                        cdate + "'),datetime('" + fdate + "'),'" + filepath + "','" + \
                        url + "',datetime('now'));"

        crsr = db.execute(sqlhas)
        nrows = crsr.fetchall()[0][0]
        if nrows == 0:
            db.execute(sqlinsert)
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
        jsondata['metget']['state'] = {'last_fetch': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       'host': socket.gethostname()}

        with open(jsonfile, 'w') as statfile:
            json.dump(jsondata, statfile, indent=1)

    def generic_status(self, table, desired_len):
        """
        Generates json status object from the avaialable NCEP-GFS data
        :return: json status object
        """
        import sqlite3
        from datetime import datetime
        db = sqlite3.connect(self.__db)

        sql = "SELECT DISTINCT FORECASTCYCLE FROM " + table + " ORDER BY FORECASTCYCLE"
        rows = db.execute(sql).fetchall()

        if len(rows) < 1:
            return {"min_forecast_date": None, "max_forecast_date": None,
                    "first_available_cycle": None, "last_available_cycle": None,
                    "latest_complete_forecast": None, "latest_complete_forecast_start": None,
                    "latest_complete_forecast_end": None, "latest_complete_forecast_length": None}

        cyc_min = rows[0][0]
        if len(rows) > 1:
            cyc_max = rows[-1][0]
        else:
            cyc_max = cyc_min
        latest_complete = None
        latest_start = None
        latest_end = None
        latest_length = None
        for r in reversed(rows):
            sql = "SELECT MIN(DATE) AS FIRST, MAX(DATE) AS LAST FROM " + table + " WHERE FORECASTCYCLE = datetime('" + \
                  r[0] + "')"
            rr = db.execute(sql).fetchall()
            start = datetime.strptime(rr[0][0], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(rr[0][1], "%Y-%m-%d %H:%M:%S")
            avail_len = (end - start).total_seconds() / 3600
            if avail_len >= desired_len:
                latest_complete = r[0]
                latest_start = start.strftime("%Y-%m-%d %H:%M:%S")
                latest_end = end.strftime("%Y-%m-%d %H:%M:%S")
                latest_length = avail_len
                break

        sql = "SELECT MIN(DATE) AS FIRST, MAX(DATE) AS LAST FROM " + table
        rows = db.execute(sql).fetchall()
        fcst_min = rows[0][0]
        fcst_max = rows[0][1]

        return {"min_forecast_date": fcst_min, "max_forecast_date": fcst_max,
                "first_available_cycle": cyc_min, "last_available_cycle": cyc_max,
                "latest_complete_forecast": latest_complete, "latest_complete_forecast_start": latest_start,
                "latest_complete_forecast_end": latest_end, "latest_complete_forecast_length": latest_length}

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
            sql = "SELECT DATE FROM hwrf WHERE stormname = '" + s["storm"] + "' ORDER BY DATE"
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

            # Backwards loop to see the most recent complete forecast cycle
            for f in reversed(rows):
                sql = "SELECT MIN(DATE) AS FIRST, MAX(DATE) AS LAST FROM hwrf WHERE stormname = '" + s[
                    "storm"] + "' AND FORECASTCYCLE = datetime('" + f[0] + "') ORDER BY DATE"
                r = db.execute(sql).fetchall()
                start = datetime.strptime(r[0][0], "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(r[0][1], "%Y-%m-%d %H:%M:%S")
                avail_len = (end - start).total_seconds() / 3600
                if avail_len >= 126:
                    latest_start = start.strftime("%Y-%m-%d %H:%M:%S")
                    latest_end = end.strftime("%Y-%m-%d %H:%M:%S")
                    latest_length = avail_len
                    latest_complete = f[0]
                    time_since_forecast = datetime.now() - datetime.strptime(f[0], "%Y-%m-%d %H:%M:%S")
                    time_since_forecast = time_since_forecast.total_seconds() / 86400
                    break

            # Assemble a storm object. We're only going to write data available in the last 10 days
            if time_since_forecast < 10:
                hwrf_stat.append(
                    {"storm": s["storm"], "min_forecast_date": fcst_min, "max_forecast_date": fcst_max,
                     "first_available_cycle": cyc_min, "last_available_cycle": cyc_max,
                     "latest_complete_forecast": latest_complete,
                     "latest_complete_forecast_start": latest_start,
                     "latest_complete_forecast_end": latest_end,
                     "latest_complete_forecast_length": latest_length})

        return hwrf_stat
