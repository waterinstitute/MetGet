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
        if not os.path.exists(self.__location + "/gfs_fcst"):
            os.mkdir(self.__location + "/gfs_fcst")
        if not os.path.exists(self.__location + "/gfs_anl"):
            os.mkdir(self.__location + "/gfs_anl")
        if not os.path.exists(self.__location + "/nam_anl"):
            os.mkdir(self.__location + "/nam_anl")
        if not os.path.exists(self.__location + "/nam_fcst"):
            os.mkdir(self.__location + "/nam_fcst")

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
        nrows = crsr.fetchall()[0][0];
        if nrows == 0:
            db.execute(sqlinsert)
            db.commit()
        db.close()
