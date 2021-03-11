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
        self.__connect()
        self.__initdatabase()

    def __connect(self):
        import pymysql
        import sys
        try:
            self.__db = pymysql.connect(host=self.__dbhost, user=self.__dbusername,
                                        passwd=self.__dbpassword, db=self.__dbname, connect_timeout=5)
            self.__cursor = self.__db.cursor()
        except pymysql.ProgrammingError as e:
            print("[ERROR]: Could not connect to MySQL database")
            print(e)
            sys.exit(1)

    def disconnect(self):
        self.__db.close()

    def __initdatabase(self):
        """
        Initializes the database with the appropriate tables
        :return:
        """

        self.__db.ping(reconnect=True)
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS gfs_ncep(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME NOT NULL, forecasttime DATETIME NOT NULL, '
            'filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS gfs_fcst(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME '
            'NOT NULL, forecasttime DATETIME NOT NULL, filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, '
            'accessed DATETIME NOT NULL);')
        # db.execute('CREATE TABLE IF NOT EXISTS nam_anl(id INTEGER PRIMARY KEY '
        #            'AUTOINCREMENT, forecastcycle DATETIME '
        #            'NOT NULL, date DATETIME NOT NULL, path STRING NOT NULL, url STRING NOT NULL, '
        #            'accessed DATETIME NOT NULL);')
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS nam_fcst(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME '
            'NOT NULL, forecasttime DATETIME NOT NULL, filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, '
            'accessed DATETIME NOT NULL);')
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS hwrf(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, stormname VARCHAR(256) NOT NULL, forecastcycle DATETIME '
            'NOT NULL, forecasttime DATETIME NOT NULL, filepath VARCHAR(256) NOT NULL, '
            'url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);')
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS nam_ncep(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, forecastcycle DATETIME NOT NULL, forecasttime DATETIME NOT NULL, '
            'filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS nhc_btk(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, storm_year INTEGER NOT NULL, basin VARCHAR(256) NOT NULL, storm INTEGER NOT NULL, '
            'advisory_start DATETIME NOT NULL, advisory_end DATETIME NOT NULL, '
            'advisory_duration_hr INT NOT NULL, filepath VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS nhc_fcst(id INTEGER PRIMARY KEY '
            'AUTO_INCREMENT, storm_year INTEGER NOT NULL, basin VARCHAR(256) NOT NULL, storm INTEGER NOT NULL, '
            'advisory VARCHAR(256) NOT NULL, advisory_start DATETIME NOT NULL, advisory_end DATETIME NOT NULL, '
            'advisory_duration_hr INT NOT NULL, filepath VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);'
        )

    def add(self, pair, datatype, filepath):
        """
        Adds a file listing to the database
        :param pair: dict containing cycledate and forecastdate
        :param datatype: The table that this file will be added to (i.e. gfsfcst)
        :param filepath: Relative file location
        :return:
        """

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
            sqlhas = "SELECT Count(*) FROM " + datatype + " WHERE year = " + str(year) + " AND ADVISORY = " + \
                     advisory + " AND BASIN = '" + basin + "' AND STORM = " + str(storm) + ";"
            sqlinsert = "INSERT INTO " + datatype + " (YEAR,BASIN,STORM,ADVISORY,ADVISORY_START,ADVISORY_END," \
                                                    "ADVISORY_DURATION_HR,PATH,ACCESSED) VALUES(" + str(year) + \
                        ",'" + basin + "'," + str(storm) + "," + advisory + ", datetime('" + start + \
                        "'), datetime('" + end + "'), " + duration + ",'" + filepath + "', datetime('now'));"
            sqlupdate = ""
        elif datatype == "nhc_btk":
            year = pair["year"]
            storm = pair["storm"]
            basin = pair["basin"]
            start = str(pair["advisory_start"])
            end = str(pair["advisory_end"])
            duration = str(pair["advisory_duration_hr"])
            sqlhas = "SELECT Count(*) FROM " + datatype + " WHERE year = " + str(
                year) + " AND BASIN = '" + basin + "' AND STORM = " + str(
                storm) + ";"
            sqlinsert = "INSERT INTO " + datatype + " (YEAR,BASIN,STORM,ADVISORY_START,ADVISORY_END," \
                                                    "ADVISORY_DURATION_HR,PATH,ACCESSED) VALUES(" + str(year) + \
                        ",'" + basin + "'," + str(storm) + ", datetime('" + start + \
                        "'), datetime('" + end + "'), " + duration + ",'" + filepath + "', datetime('now'));"
            sqlupdate = "UPDATE " + datatype + " SET ACCESSED = datetime('now') WHERE year = " + str(
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

        self.__db.ping(reconnect=True)
        self.__cursor.execute(sqlhas)
        nrows = self.__cursor.fetchone()[0]
        if nrows == 0:
            print("Inserting "+filepath+" into database (Cycle="+str(cdate)+", ForecastDate="+str(fdate)+")")
            self.__cursor.execute(sqlinsert)
            self.__db.commit()
