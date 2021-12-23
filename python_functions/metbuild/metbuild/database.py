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

    def generate_file_list(self, service, start, end, storm, nowcast, multiple_forecasts):
        import sys
        if service == "gfs-ncep":
            return self.generate_generic_file_list("gfs_ncep", start, end, nowcast, multiple_forecasts)
        elif service == "nam-ncep":
            return self.generate_generic_file_list("nam_ncep", start, end, nowcast, multiple_forecasts)
        elif service == "hwrf":
            return self.generate_hwrf_file_list(start, end, storm)
        else:
            print("ERROR: Invalid data type")
            sys.exit(1)

    def generate_generic_file_list(self, table, start, end, nowcast, multiple_forecasts):
        from datetime import timedelta
        if nowcast:
            return self.generate_generic_file_list_nowcast(table, start, end)
        else:
            if multiple_forecasts:
                return self.generate_generic_file_list_multiple_forecasts(table, start, end)
            else:
                return self.generate_generic_file_list_single_forecast(table, start, end)

    def generate_generic_file_list_nowcast(self, table, start, end):
        sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from " + table + \
             " t1 JOIN(select forecasttime, max(id) id FROM "+table+" group by forecasttime order by forecasttime) t2 " \
             "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecastcycle >= '" + start.strftime(
             "%Y-%m-%d %H:%M:%S") + "' AND t1.forecastcycle <= '" + end.strftime(
             "%Y-%m-%d %H:%M:%S") + "' AND t1.forecastcycle = t1.forecasttime;"
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3]])
        return return_list

    def generate_generic_file_list_multiple_forecasts(self, table, start, end):
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


    def generate_generic_file_list_single_forecast(self, table, start, end):
        sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from " + table + \
              " t1 JOIN(select forecasttime, max(id) id FROM "+table+" group by forecasttime order by forecasttime) t2 " \
              "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '" + start.strftime(
              "%Y-%m-%d %H:%M:%S") + "' AND t1.forecasttime <= '" + end.strftime(
              "%Y-%m-%d %H:%M:%S") + "';"
        self.cursor().execute(sql)
        row = self.cursor().fetchone()

        first_time = row[1]

        sql = "select id,forecastcycle,forecasttime,filepath from " + table + \
                " where forecastcycle = '"+first_time.strftime("%Y-%m-%d %H:%M:%S")+"' AND forecasttime >= '"+ \
                start.strftime("%Y-%m-%d %H:%M:%S") + "' AND forecasttime <= '" + end.strftime("%Y-%m-%d %H:%M:%S")+ \
                "' order by forecasttime;"
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3]])
        return return_list


    def generate_hwrf_file_list(self, start, end, storm):

       # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        sql_tmptable = "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from hwrf where stormname = '"+storm+"';"
        sql_tmptable2 = "create temporary table tmptbl2 select * from tmptbl1;"
        sql = "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1 " \
             " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2 group by forecasttime order by forecasttime) t2 " \
             "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '" + start.strftime(
             "%Y-%m-%d %H:%M:%S") + "' AND t1.forecasttime <= '" + end.strftime(
             "%Y-%m-%d %H:%M:%S") + "';"

        self.cursor().execute(sql_tmptable)
        self.cursor().execute(sql_tmptable2)
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3]])
        return return_list

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

    def generate_request_table(self):
        sql = "create table if not exists requests(id INTEGER PRIMARY KEY AUTO_INCREMENT, request_id VARCHAR(36) not null, try INTEGER default 0, status enum('running', 'error', 'completed') not null, message VARCHAR(1024), start_date DATETIME not null, last_date DATETIME not null, input_data VARCHAR(8096));"
        self.cursor().execute(sql)

    def query_request_status(self,request_id):
        self.generate_request_table()
        sql = "select try, status, message from requests where request_id = '"+request_id+"';" 
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()

        if len(rows) == 0:
            return {"request": request_id, "try": 0, "status": "unknown", "message": "request_not_found"}
        else:
            return {"request": request_id, "try": rows[0][0], "status": rows[0][1], "message": rows[0][2]}

    def update_request_status(self, request_id, status, message, json, istry=False):
        from datetime import datetime
        self.generate_request_table()
        response = self.query_request_status(request_id)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if response["try"] == 0:
            sql = "INSERT INTO requests (request_id, try, status, message, start_date, last_date, input_data) values('"+request_id+"',1,'"+status+"','"+message+"','"+now+"','"+now+"','"+json+"');"
        else:
            if istry:
                sql = "UPDATE requests SET try = "+str(response["try"]+1)+", status = '"+status+"', message = '"+message+"', last_date = '"+now+"' where request_id = '"+request_id+"';"
            else:
                sql = "UPDATE requests SET status = '"+status+"', message = '"+message+"', last_date = '"+now+"' where request_id = '"+request_id+"';"

        self.cursor().execute(sql)
        self.__db.commit()


