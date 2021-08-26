class Database:
    def __init__(self):
        import sys
        import pymysql
        from pymysql import MySQLError
        import boto3
        import os
        self.__dbhost = os.environ["DBSERVER"]
        self.__dbpassword = os.environ["DBPASS"]
        self.__dbusername = os.environ["DBUSER"]
        self.__dbname = os.environ["DBNAME"]
        self.__bucket = os.environ["BUCKET"]
        self.__s3client = boto3.client("s3")
        try:
            self.__db = pymysql.connect(host=self.__dbhost,
                                        user=self.__dbusername,
                                        passwd=self.__dbpassword,
                                        db=self.__dbname,
                                        connect_timeout=5)
            self.__cursor = self.__db.cursor()
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            sys.exit(1)

    def cursor(self):
        return self.__cursor

    def s3client(self):
        return self.__s3client

    def bucket(self):
        return self.__bucket

    def generate_file_list(self, service, start, end, storm=None):
        if service == "gfs-ncep":
            return self.generate_generic_file_list("gfs_ncep", start, end)
        elif service == "nam-ncep":
            return self.generate_generic_file_list("nam_ncep", start, end)
        elif service == "hwrf":
            return self.generate_hwrf_file_list(start, end, storm)
        else:
            print("ERROR: Invalid data type")
            sys.exit(1)

    def generate_generic_file_list(self, table, start, end, nowcast, multiple_forecasts):
        from datetime import timedelta
        if nowcast:
            sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from " + table + \
                  " t1 JOIN(select forecasttime, max(id) id FROM "+table+" group by forecasttime order by forecasttime) t2 " \
                  "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecastcycle >= '" + start.strftime(
                  "%Y-%m-%d %H:%M:%S") + "' AND t1.forecastcycle <= '" + end.strftime(
                  "%Y-%m-%d %H:%M:%S") + " AND t1.forecastcycle == t1.forecasttime';"
        else:
            if multiple_forecasts:
                sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from " + table + \
                      " t1 JOIN(select forecasttime, max(id) id FROM "+table+" group by forecasttime order by forecasttime) t2 " \
                      "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '" + start.strftime(
                      "%Y-%m-%d %H:%M:%S") + "' AND t1.forecasttime <= '" + end.strftime(
                      "%Y-%m-%d %H:%M:%S") + "';"
            else:
                sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from " + table + \
                      " t1 JOIN(select forecasttime, max(id) id FROM "+table+" group by forecasttime order by forecasttime) t2 " \
                      "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '" + start.strftime(
                      "%Y-%m-%d %H:%M:%S") + "' AND t1.forecasttime <= '" + end.strftime(
                      "%Y-%m-%d %H:%M:%S") + "';"

        print(self.__dbhost)
        print(self.__dbserver)
        print(self.__dbname)
        print(self.__dbpass)
        print(sql)

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
