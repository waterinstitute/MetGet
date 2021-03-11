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
class Database:
    def __init__(self):
        import sys
        import pymysql
        import boto3
        self.__dbhost = os.environ["DBSERVER"]
        self.__dbpassword = os.environ["DBPASS"]
        self.__dbusername = os.environ["DBUSER"]
        self.__dbname = os.environ["DBNAME"]
        self.__s3client = boto3.client("s3")
        try:
            self.__db = pymysql.connect(self.__dbhost,
                                        user=self.__dbusername,
                                        passwd=self.__dbpassword,
                                        db=self.__dbname,
                                        connect_timeout=5)
            self.__cursor = self.__db.cursor()
        except:
            print("[ERROR]: Could not connect to MySQL database")
            sys.exit(1)

    def cursor(self):
        return self.__cursor

    def s3client(self):
        return self.__s3client

    def bucket(self):
        return self.__bucket

    def generate_file_list(self, service, start, end, storm=None):
        if service == "gfs":
            return self.generate_generic_file_list("gfs_ncep", start, end)
        elif service == "nam":
            return self.generate_generic_file_list("nam_ncep", start, end)
        elif service == "hwrf":
            return self.generate_hwrf_file_list(start, end, storm)

    def generate_generic_file_list(self, table, start, end):
        from datetime import timedelta
        sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from " + table + \
              " t1 JOIN(select forecasttime, max(id) id FROM "+table+" group by forecasttime order by forecasttime) t2 " \
              "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '" + start.strftime(
            "%Y-%m-%d %H:%M:%S") + "' AND t1.forecasttime <= '" + end.strftime(
            "%Y-%m-%d %H:%M:%S") + "';"
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3]])
        return return_list

    def generate_hwrf_file_list(self, start, end, storm):
        return None

    def get_file(self, db_path, service, time, dry_run=False):
        import tempfile
        import os
        fn = db_path.split("/")[-1]
        local_path = tempfile.gettempdir(
        ) + "/" + service + "." + time.strftime("%Y%m%d%H%M") + "." + fn
        if not dry_run:
            if not os.path.exists(local_path):
                self.s3client().download_file(self.bucket(), db_path,
                                              local_path)
        return local_path
