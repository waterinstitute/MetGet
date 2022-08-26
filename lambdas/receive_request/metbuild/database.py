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
        self.__bucket = os.environ["BUCKET_NAME"]
        self.__s3client = boto3.client("s3")
        try:
            self.__db = pymysql.connect(
                host=self.__dbhost,
                user=self.__dbusername,
                passwd=self.__dbpassword,
                db=self.__dbname,
                connect_timeout=5,
            )
            self.__cursor = self.__db.cursor()
        except MySQLError as e:
            print("Got error {!r}, errno is {}".format(e, e.args[0]))
            sys.exit(1)

    def cursor(self):
        return self.__cursor

    def s3client(self):
        return self.__s3client

    def bucket(self):
        return self.__bucket

    def generate_file_list(
        self,
        service,
        param,
        start,
        end,
        storm,
        nowcast,
        multiple_forecasts,
        ensemble_member,
    ):
        import sys

        if service == "gfs-ncep":
            return self.generate_generic_file_list(
                "gfs_ncep", param, start, end, nowcast, multiple_forecasts
            )
        elif service == "nam-ncep":
            return self.generate_generic_file_list(
                "nam_ncep", param, start, end, nowcast, multiple_forecasts
            )
        elif service == "hwrf":
            return self.generate_storm_file_list(
                "hwrf", start, end, storm, nowcast, multiple_forecasts
            )
        elif service == "coamps-tc":
            return self.generate_storm_file_list(
                "coamps_tc", start, end, storm, nowcast, multiple_forecasts
            )
        elif service == "gefs-ncep":
            return self.generate_gefs_file_list(
                ensemble_member, start, end, nowcast, multiple_forecasts
            )
        else:
            print("ERROR: Invalid data type")
            sys.exit(1)

    def generate_generic_file_list(
        self, table, param, start, end, nowcast, multiple_forecasts
    ):
        if nowcast:
            return self.generate_generic_file_list_nowcast(table, start, end)
        else:
            if multiple_forecasts:
                return self.generate_generic_file_list_multiple_forecasts(
                    table, start, end
                )
            else:
                return self.generate_generic_file_list_single_forecast(
                    table, start, end
                )

    def generate_generic_file_list_nowcast(self, table, start, end):
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from "
            + table
            + " t1 JOIN(select forecasttime, max(id) id FROM "
            + table
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecastcycle >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecastcycle <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecastcycle = t1.forecasttime;"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3], f[1]])
        return return_list

    def generate_generic_file_list_multiple_forecasts(self, table, start, end):
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from "
            + table
            + " t1 JOIN(select forecasttime, max(id) id FROM "
            + table
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3], f[1]])
        return return_list

    def generate_generic_file_list_single_forecast(self, table, start, end):
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from "
            + table
            + " t1 JOIN(select forecasttime, max(id) id FROM "
            + table
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql)
        row = self.cursor().fetchone()

        first_time = row[1]

        sql = (
            "select id,forecastcycle,forecasttime,filepath from "
            + table
            + " where forecastcycle = '"
            + first_time.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "' order by forecasttime;"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3], f[1]])
        return return_list

    def generate_storm_file_list(
        self, data_type, start, end, storm, nowcast, multiple_forecasts
    ):
        if nowcast:
            return self.generate_storm_file_list_nowcast(data_type, start, end, storm)
        else:
            if multiple_forecasts:
                return self.generate_storm_file_list_multiple_forecasts(
                    data_type, start, end, storm
                )
            else:
                return self.generate_storm_file_list_single_forecast(
                    data_type, start, end, storm
                )

    def generate_storm_file_list_nowcast(self, data_type, start, end, storm):
        # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        sql_tmptable = (
            "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from "
            + data_type
            + " where stormname = '"
            + storm
            + "';"
        )
        sql_tmptable2 = "create temporary table tmptbl2 select * from tmptbl1;"
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1"
            " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2 group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecastcycle >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecastcycle <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecastcycle = t1.forecasttime;"
        )
        self.cursor().execute(sql_tmptable)
        self.cursor().execute(sql_tmptable2)
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []

        if rows:
            for f in rows:
                return_list.append([f[2], f[3], f[1]])

        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_storm_file_list_single_forecast(self, data_type, start, end, storm):
        # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        sql_tmptable = (
            "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from "
            + data_type
            + " where stormname = '"
            + storm
            + "';"
        )
        sql_tmptable2 = "create temporary table tmptbl2 select * from tmptbl1;"
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1"
            " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2 group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql_tmptable)
        self.cursor().execute(sql_tmptable2)
        self.cursor().execute(sql)
        row = self.cursor().fetchone()

        if row:
            first_time = row[1]
        else:
            self.cursor().execute("drop temporary table tmptbl1;")
            self.cursor().execute("drop temporary table tmptbl2;")
            return []

        sql = (
            "select id,forecastcycle,forecasttime,filepath from tmptbl1"
            " where forecastcycle = '"
            + first_time.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "' order by forecasttime;"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []

        if rows:
            for f in rows:
                return_list.append([f[2], f[3], f[1]])

        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_storm_file_list_multiple_forecasts(self, data_type, start, end, storm):
        # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        sql_tmptable = (
            "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from "
            + data_type
            + " where stormname = '"
            + storm
            + "';"
        )
        sql_tmptable2 = "create temporary table tmptbl2 select * from tmptbl1;"
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1"
            " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2 group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql_tmptable)
        self.cursor().execute(sql_tmptable2)
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []

        if rows:
            for f in rows:
                return_list.append([f[2], f[3], f[1]])
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def get_file(self, db_path, service, time, dry_run=False):
        import tempfile
        import os

        fn = db_path.split("/")[-1]
        local_path = (
            tempfile.gettempdir()
            + "/"
            + service
            + "."
            + time.strftime("%Y%m%d%H%M")
            + "."
            + fn
        )
        if not dry_run:
            if not os.path.exists(local_path):
                self.s3client().download_file(self.bucket(), db_path, local_path)
        return local_path

    def generate_request_table(self):
        sql = "create table if not exists requests(id INTEGER PRIMARY KEY AUTO_INCREMENT, request_id VARCHAR(36) not null, try INTEGER default 0, status enum('queued', 'running', 'error', 'completed') not null, message VARCHAR(1024), start_date DATETIME not null, last_date DATETIME not null, api_key VARCHAR(128), source_ip VARCHAR(128), input_data VARCHAR(8096));"
        self.cursor().execute(sql)

    def add_request_to_queue(self, request_id, json_data):
        from datetime import datetime
        import json

        api_key = json_data["api-key"]
        source_ip = json_data["source-ip"]

        self.generate_request_table()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = (
            "INSERT INTO requests (request_id, try, status, message, start_date, last_date, api_key, source_ip, input_data) values('"
            + request_id
            + "',0,'queued','Message has been added to queue','"
            + now
            + "','"
            + now
            + "','"
            + api_key
            + "','"
            + source_ip
            + "','"
            + json.dumps(json_data)
            + "');"
        )
        self.cursor().execute(sql)
        self.__db.commit()

    def check_apikey_authorized(self, key, service) -> bool:
        service_dict = {"gfs-ncep": 3, "nam-ncep": 4, "hwrf": 5, "coamps-tc": 6}
        sql = "select * from apikey_authorization where apikey = '{}';".format(key)
        self.cursor().execute(sql)
        row = self.cursor().fetchone()

        if not row:
            return True

        if row[2] == 1:
            return True

        if service not in service_dict.keys():
            return True

        index = service_dict[service]
        print(index)
        if row[index] == 1:
            return True
        else:
            return False

    def generate_gefs_file_list(
        self, ensemble_member, start, end, nowcast, multiple_forecasts
    ):
        table = "gefs-fcst"
        if nowcast:
            return self.generate_gefs_file_list_nowcast(
                table, ensemble_member, start, end
            )
        else:
            if multiple_forecasts:
                return self.generate_gefs_file_list_multiple_forecasts(
                    table, ensemble_member, start, end
                )
            else:
                return self.generate_gefs_file_list_single_forecast(
                    table, ensemble_member, start, end
                )

    def generate_gefs_file_list_nowcast(self, table, ensemble_member, start, end):
        sql = (
            "select t1.id,t1.ensemble_member,t1.forecastcycle,t1.forecasttime,t1.filepath from "
            + table
            + " t1 JOIN(select forecasttime, max(id) id FROM "
            + table
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.ensemble_member = '"
            + ensemble_member
            + "' AND t1.forecasttime = t2.forecasttime AND t1.forecastcycle >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecastcycle <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecastcycle = t1.forecasttime;"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3], f[1]])
        return return_list

    def generate_gefs_file_list_multiple_forecasts(
        self, table, ensemble_member, start, end
    ):
        sql = (
            "select t1.id,t1.ensemble_member,t1.forecastcycle,t1.forecasttime,t1.filepath from "
            + table
            + " t1 JOIN(select forecasttime, max(id) id FROM "
            + table
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.ensemble_member = '"
            + ensemble_member
            + "' AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3], f[1]])
        return return_list

    def generate_gefs_file_list_single_forecast(
        self, table, ensemble_member, start, end
    ):
        sql = (
            "select t1.id,t1.ensemble_member,t1.forecastcycle,t1.forecasttime,t1.filepath from "
            + table
            + " t1 JOIN(select forecasttime, max(id) id FROM "
            + table
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id AND t1.ensemble_member = '"
            + ensemble_member
            + "' AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql)
        row = self.cursor().fetchone()

        first_time = row[1]

        sql = (
            "select id,ensemble_member,forecastcycle,forecasttime,filepath from "
            + table
            + " where ensemble_member = '"
            + ensemble_member
            + "' AND forecastcycle = '"
            + first_time.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "' order by forecasttime;"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3], f[1]])
        return return_list
