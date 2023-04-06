import psycopg2
import boto3
from datetime import datetime
import logging


class Database:
    """
    Class to handle database connections for metget
    """

    def __init__(self):
        """
        Initialize the database connection
        """
        import os

        self.__dbhost = os.environ["METGET_DATABASE_SERVICE_HOST"]
        self.__dbpassword = os.environ["METGET_DATABASE_PASSWORD"]
        self.__dbusername = os.environ["METGET_DATABASE_USER"]
        self.__dbname = os.environ["METGET_DATABASE"]
        self.__bucket = os.environ["METGET_S3_BUCKET"]
        self.__s3client = boto3.client("s3")

        self.__db = psycopg2.connect(
            host=self.__dbhost,
            database=self.__dbname,
            user=self.__dbusername,
            password=self.__dbpassword,
        )
        self.__cursor = self.__db.cursor()

    def cursor(self) -> psycopg2.cursor:
        """
        Return the database cursor
        """
        return self.__cursor

    def s3client(self) -> boto3.client:
        """
        Return the s3 client
        """
        return self.__s3client

    def bucket(self) -> str:
        """
        Return the s3 bucket name
        """
        return self.__bucket

    def generate_file_list(
        self,
        service,
        param,
        start,
        end,
        storm,
        basin,
        advisory,
        tau,
        nowcast,
        multiple_forecasts,
        ensemble_member=None,
    ) -> any:
        """
        Generate a list of files to download

        Args:
            service (str): The data service to use
            param (str): The parameter to download
            start (datetime): The start time
            end (datetime): The end time
            storm (str): The storm name
            basin (str): The storm basin
            advisory (int): The advisory number
            tau (int): The forecast lead time
            nowcast (bool): Whether to download nowcast data
            multiple_forecasts (bool): Whether to download multiple forecasts
            ensemble_member (str): The ensemble member to download

        Returns:
            A list of files to download
        """

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
                "hwrf", param, start, end, storm, nowcast, multiple_forecasts
            )
        elif service == "coamps-tc":
            return self.generate_storm_file_list(
                "coamps_tc", param, start, end, storm, nowcast, multiple_forecasts, tau
            )
        elif service == "gefs-ncep":
            if not ensemble_member:
                raise RuntimeError("ERROR: No ensemble member specified")
            return self.generate_gefs_file_list(
                ensemble_member, start, end, nowcast, multiple_forecasts
            )
        elif service == "nhc":
            if not basin:
                raise RuntimeError("ERROR: Must specify basin")
            if not storm:
                raise RuntimeError("ERROR: Must specify storm")
            if not advisory:
                raise RuntimeError("ERROR: Must specify advisory")
            year = start.year
            return self.generate_nhc_file_list(year, basin, storm, advisory)
        else:
            raise RuntimeError("ERROR: Invalid data type")

    def generate_nhc_file_list(
        self, year: int, basin: str, storm: str, advisory: int
    ) -> dict:
        """
        Generate a list of files to download for NHC data

        Args:
            year (int): The year of the storm
            basin (str): The basin of the storm
            storm (str): The name of the storm
            advisory (int): The advisory number

        Returns:
            A dictionary containing the best track and forecast track file paths

        """
        best_track_table = "nhc_btk"
        best_track_sql = "select * from {:s} where storm_year = '{:04d}' and basin = '{:s}' and storm = '{:s}';".format(
            best_track_table, year, basin, storm
        )

        self.cursor().execute(best_track_sql)
        rows = self.cursor().fetchone()
        if rows:
            btk_filepath = rows[7]
            btk_start = rows[4]
            btk_end = rows[5]
            btk_duration = rows[6]
            best_track = {
                "start": btk_start,
                "end": btk_end,
                "duration": btk_duration,
                "filepath": btk_filepath,
            }
        else:
            best_track = None

        if not advisory == 0:
            forecast_table = "nhc_fcst"
            forecast_sql = (
                "select * from {:s} where storm_year = "
                "'{:04d}' and basin = '{:s}' and storm = "
                "'{:s}' and advisory = '{:d}';".format(
                    forecast_table, year, basin, storm, advisory
                )
            )
            self.cursor().execute(forecast_sql)
            rows = self.cursor().fetchone()
            if rows:
                fcst_filepath = rows[8]
                fcst_duration = rows[7]
                fcst_start = rows[5]
                fcst_end = rows[6]
                fcst_track = {
                    "start": fcst_start,
                    "end": fcst_end,
                    "duration": fcst_duration,
                    "filepath": fcst_filepath,
                }
            else:
                fcst_track = None
        else:
            fcst_track = None

        return {"best_track": best_track, "forecast_track": fcst_track}

    def generate_generic_file_list(
        self,
        table: str,
        param_type: str,
        start: datetime,
        end: datetime,
        nowcast: bool,
        multiple_forecasts: bool,
    ) -> list:
        """
        Generate a list of files to download for generic data (i.e. gfs, nam, etc)

        Args:
            table (str): The database table to use
            param_type (str): The parameter type to download
            start (datetime): The start time
            end (datetime): The end time
            nowcast (bool): Whether to download nowcast data
            multiple_forecasts (bool): Whether to download multiple forecasts

        Returns:
            A list of files to download
        """

        if table == "nam_ncep" and param_type == "rain":
            return self.generate_generic_file_list_ignore_zero_hour(table, start, end)
        else:
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

    def generate_generic_file_list_ignore_zero_hour(
        self, table: str, start: datetime, end: datetime
    ) -> list:
        """
        This is a very specific use case. The NAM model doesn't report precip rate in the operational setting
        so we need to use accumulated precip, however, at the zero hour, no precip has accumulated. Rather than
        constantly interpolating to/from zero, we will just ignore zero hour forecasts when the rainfall is requested
        from the NAM model

        Args:
            table (str): The database table to use
            start (datetime): The start time
            end (datetime): The end time

        Returns:
            A list of files to download

        """
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
            + "' AND t1.forecastcycle != t1.forecasttime;"
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()
        return_list = []
        for f in rows:
            return_list.append([f[2], f[3]])
        return return_list

    def generate_generic_file_list_nowcast(
        self, table: str, start: datetime, end: datetime
    ) -> list:
        """
        Generate a list of files to download for generic data (i.e. gfs, nam, etc) for nowcast data

        Args:
            table (str): The database table to use
            start (datetime): The start time
            end (datetime): The end time

        Returns:
            A list of files to download
        """
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
            return_list.append([f[2], f[3]])
        return return_list

    def generate_generic_file_list_multiple_forecasts(
        self, table: str, start: datetime, end: datetime
    ) -> list:
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
            return_list.append([f[2], f[3]])
        return return_list

    def generate_generic_file_list_single_forecast(
        self, table: str, start: datetime, end: datetime
    ):
        """
        Generate a list of files to download for generic data (i.e. gfs, nam, etc) for a single forecast

        Args:
            table (str): The database table to use
            start (datetime): The start time
            end (datetime): The end time

        Returns:
            A list of files to download
        """
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
            return_list.append([f[2], f[3]])
        return return_list

    def generate_gefs_file_list(
        self,
        ensemble_member: str,
        start: datetime,
        end: datetime,
        nowcast: bool,
        multiple_forecasts: bool,
    ) -> list:
        """
        Generate a list of files to download for GEFS data

        Args:
            ensemble_member (str): The ensemble member to download
            start (datetime): The start time
            end (datetime): The end time
            nowcast (bool): If True, download nowcast data
            multiple_forecasts (bool): If True, download multiple forecasts

        Returns:
            A list of files to download

        """
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

    def generate_gefs_file_list_nowcast(
        self, table: str, ensemble_member: str, start: datetime, end: datetime
    ):
        """
        Generate a list of files to download for GEFS nowcast data

        Args:
            table (str): The database table to use (unused)
            ensemble_member (str): The ensemble member to download
            start (datetime): The start time
            end (datetime): The end time

        Returns:
            A list of files to download
        """
        sql_tmptbl = "create temporary table tmptbl1 select * from gefs_fcst where ensemble_member = '{:s}';".format(
            ensemble_member
        )
        sql_tmptbl2 = "create temporary table tmptbl2 select * from gefs_fcst where ensemble_member = '{:s}';".format(
            ensemble_member
        )
        self.cursor().execute(sql_tmptbl)
        self.cursor().execute(sql_tmptbl2)
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1"
            + " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2"
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id"
            + " AND t1.forecasttime = t2.forecasttime AND t1.forecastcycle >= '"
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
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_gefs_file_list_multiple_forecasts(
        self, table: str, ensemble_member: str, start: datetime, end: datetime
    ):
        """
        Generate a list of files to download for GEFS multiple forecasts data

        Args:
            table (str): The database table to use (unused)
            ensemble_member (str): The ensemble member to download
            start (datetime): The start time
            end (datetime): The end time

        Returns:
            A list of files to download
        """
        sql_tmptbl = "create temporary table tmptbl1 select * from gefs_fcst where ensemble_member = '{:s}';".format(
            ensemble_member
        )
        sql_tmptbl2 = "create temporary table tmptbl2 select * from gefs_fcst where ensemble_member = '{:s}';".format(
            ensemble_member
        )
        self.cursor().execute(sql_tmptbl)
        self.cursor().execute(sql_tmptbl2)
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1"
            + " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2"
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id"
            + " AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
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
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_gefs_file_list_single_forecast(
        self, table: str, ensemble_member: str, start: datetime, end: datetime
    ):
        """
        Generate a list of files to download for GEFS single forecast data

        Args:
            table (str): The database table to use (unused)
            ensemble_member (str): The ensemble member to download
            start (datetime): The start time
            end (datetime): The end time

        Returns:
            A list of files to download

        """
        sql_tmptbl = "create temporary table tmptbl1 select * from gefs_fcst where ensemble_member = '{:s}';".format(
            ensemble_member
        )
        sql_tmptbl2 = "create temporary table tmptbl2 select * from gefs_fcst where ensemble_member = '{:s}';".format(
            ensemble_member
        )
        self.cursor().execute(sql_tmptbl)
        self.cursor().execute(sql_tmptbl2)
        sql = (
            "select t1.id,t1.forecastcycle,t1.forecasttime,t1.filepath from tmptbl1"
            + " t1 JOIN(select forecasttime, max(id) id FROM tmptbl2"
            + " group by forecasttime order by forecasttime) t2 "
            "ON t1.id = t2.id"
            + " AND t1.forecasttime = t2.forecasttime AND t1.forecasttime >= '"
            + start.strftime("%Y-%m-%d %H:%M:%S")
            + "' AND t1.forecasttime <= '"
            + end.strftime("%Y-%m-%d %H:%M:%S")
            + "';"
        )
        self.cursor().execute(sql)
        row = self.cursor().fetchone()

        first_time = row[1]

        sql = (
            "select id,forecastcycle,forecasttime,filepath from tmptbl1"
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
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_storm_file_list(
        self,
        data_type: str,
        param_type: str,
        start: datetime,
        end: datetime,
        storm: str,
        nowcast: bool,
        multiple_forecasts: bool,
        tau=0,
    ):
        """
        Generate a list of files to download for a storm event

        Args:
            data_type (str): The data type to download (gfs, gefs, etc)
            param_type (str): The parameter type to download (rain, wind, etc)
            start (datetime): The start time
            end (datetime): The end time
            storm (str): The storm name
            nowcast (bool): Whether or not to download nowcast data
            multiple_forecasts (bool): Whether or not to download multiple forecasts
            tau (int): The forecast hour to download

        Returns:
            A list of files to download
        """
        if param_type == "rain" and tau == 0:
            tau = 1

        if nowcast:
            return self.generate_storm_file_list_nowcast(data_type, start, end, storm)
        else:
            if multiple_forecasts:
                return self.generate_storm_file_list_multiple_forecasts(
                    data_type, start, end, storm, tau
                )
            else:
                return self.generate_storm_file_list_single_forecast(
                    data_type, start, end, storm, tau
                )

    def generate_storm_file_list_nowcast(
        self, data_type: str, start: datetime, end: datetime, storm: str
    ) -> list:
        """
        Generate a list of files to download for a storm event nowcast data

        Args:
            data_type (str): The data type to download (gfs, gefs, etc)
            start (datetime): The start time
            end (datetime): The end time
            storm (str): The storm name

        Returns:
            A list of files to download

        """
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
        for f in rows:
            return_list.append([f[2], f[3]])
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_storm_file_list_ignore_zero_hour(
        self, data_type: str, start: datetime, end: datetime, storm: str
    ):
        """
        Generate a list of files to download for a storm event nowcast data ignoring the zero hour forecast

        Args:
            data_type (str): The data type to download (gfs, gefs, etc)
            start (datetime): The start time
            end (datetime): The end time
            storm (str): The storm name

        Returns:
            A list of files to download
        """
        # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        sql_tmptable = (
            "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from "
            + data_type
            + " where stormname = '"
            + storm
            + "'AND forecastcycle != forecasttime;"
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
        for f in rows:
            return_list.append([f[2], f[3]])
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_storm_file_list_single_forecast(
        self, data_type: str, start, end, storm: str, tau: int
    ) -> list:
        """
        Generate a list of files to download for a storm event single forecast data

        Args:
            data_type (str): The data type to download (gfs, gefs, etc)
            start (datetime): The start time
            end (datetime): The end time
            storm (str): The storm name
            tau (int): The forecast hour

        Returns:
            A list of files to download

        """
        # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        if tau > 0 and data_type == "coamps_tc":
            sql_tmptable = (
                "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from "
                + data_type
                + " where stormname = '"
                + storm
                + "' and tau >= {:d}".format(tau)
                + ";"
            )
        else:
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

        first_time = row[1]

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
        for f in rows:
            return_list.append([f[2], f[3]])
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def generate_storm_file_list_multiple_forecasts(
        self, data_type: str, start: datetime, end: datetime, storm: str, tau: int
    ) -> list:
        """
        Generate a list of files to download for a storm event multiple forecast data

        Args:
            data_type (str): The data type to download (gfs, gefs, etc)
            start (datetime): The start time
            end (datetime): The end time
            storm (str): The storm name
            tau (int): The forecast hour

        Returns:
            A list of files to download
        """
        # ... Generate some selections into a temporary table. This essentially duplicates the gfs style database
        if tau > 0 and data_type == "coamps_tc":
            sql_tmptable = (
                "create temporary table tmptbl1 select id,forecastcycle,forecasttime,filepath from "
                + data_type
                + " where stormname = '"
                + storm
                + "' and tau >= {:d}".format(tau)
                + ";"
            )
        else:
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
        for f in rows:
            return_list.append([f[2], f[3]])
        self.cursor().execute("drop temporary table tmptbl1;")
        self.cursor().execute("drop temporary table tmptbl2;")
        return return_list

    def check_archive_status(self, filepath: str) -> bool:
        """
        Check the archive status of a file

        Args:
            filepath (str): The file path to check

        Returns:
            True if archived, False if not
        """
        metadata = self.s3client().head_object(Bucket=self.bucket(), Key=filepath)
        if "x-amz-archive-status" in metadata["ResponseMetadata"]["HTTPHeaders"].keys():
            access = metadata["ResponseMetadata"]["HTTPHeaders"]["x-amz-archive-status"]
            return True
        else:
            return False

    def check_ongoing_restore(self, filepath: str) -> bool:
        """
        Check if a restore is ongoing for a file

        Args:
            filepath (str): The file path to check

        Returns:
            True if ongoing, False if not
        """
        metadata = self.s3client().head_object(Bucket=self.bucket(), Key=filepath)
        if "x-amz-restore" in metadata["ResponseMetadata"]["HTTPHeaders"].keys():
            ongoing = metadata["ResponseMetadata"]["HTTPHeaders"]["x-amz-restore"]
            if ongoing == 'ongoing-request="true"':
                return True
            else:
                return False
        else:
            return False

    def initiate_restore(self, filepath: str) -> None:
        """
        Initiate a restore for a file

        Args:
            filepath (str): The file path to restore

        Returns:
            None
        """

        log = logging.getLogger(__name__)

        ongoing = self.check_ongoing_restore(filepath)
        if not ongoing:
            response = self.s3client().restore_object(
                Bucket=self.bucket(),
                Key=filepath,
                RestoreRequest={"GlacierJobParameters": {"Tier": "Standard"}},
            )
            log.info("Initiating restore for file: " + filepath)
        else:
            log.info("Ongoing restore for file: " + filepath)

    def check_initiate_restore(
        self, db_path: str, service: str, time: datetime, dry_run: bool = False
    ) -> bool:
        """
        Check if a restore is needed and initiate it if not

        Args:
            db_path (str): The database path
            service (str): The service name
            time (datetime): The time of the file
            dry_run (bool): If True, don't initiate a restore

        Returns:
            True if a restore was initiated, False if not
        """
        if dry_run:
            return False
        archive_status = self.check_archive_status(db_path)
        if archive_status:
            self.initiate_restore(db_path)
            return True
        return False

    def get_file(
        self, db_path: str, service: str, time: datetime = None, dry_run: bool = False
    ):
        """
        Get a file from the database

        Args:
            db_path (str): The database path
            service (str): The service name
            time (datetime): The time of the file
            dry_run (bool): If True, don't download the file

        Returns:
            The local path to the file
        """
        import tempfile
        import os

        fn = db_path.split("/")[-1]
        if time:
            local_path = (
                tempfile.gettempdir()
                + "/"
                + service
                + "."
                + time.strftime("%Y%m%d%H%M")
                + "."
                + fn
            )
        else:
            local_path = tempfile.gettempdir() + "/" + fn
        if not dry_run:
            if not os.path.exists(local_path):
                self.s3client().download_file(self.bucket(), db_path, local_path)
        return local_path

    def query_request_status(self, request_id: str):
        """
        Query the status of a request

        Args:
            request_id (str): The request id

        Returns:
            A dictionary with the request status
        """
        sql = "select try, status, message from requests where request_id = '{:s}';".format(
            request_id
        )
        self.cursor().execute(sql)
        rows = self.cursor().fetchall()

        if len(rows) == 0:
            return {
                "request": request_id,
                "try": 0,
                "status": "unknown",
                "message": "request_not_found",
            }
        else:
            return {
                "request": request_id,
                "try": rows[0][0],
                "status": rows[0][1],
                "message": rows[0][2],
            }

    def update_request_status(
        self,
        request_id: str,
        status: str,
        message: str,
        jsonstr: str,
        istry: bool = False,
        decrement: bool = False,
    ) -> None:
        """
        Update the status of a request

        Args:
            request_id (str): The request id
            status (str): The status
            message (str): The message
            jsonstr (str): The json string
            istry (bool): If True, increment the try counter
            decrement (bool): If True, decrement the try counter

        Returns:
            None
        """
        from datetime import datetime
        import json

        response = self.query_request_status(request_id)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if response["status"] == "unknown":
            jsondata = json.loads(jsonstr)
            apikey = jsondata["api-key"]
            sourceip = jsondata["source-ip"]
            sql = (
                "INSERT INTO requests (request_id, try, status, message, api_key, source_ip, start_date, last_date, input_data) values('"
                + request_id
                + "',1,'"
                + status
                + "','"
                + message
                + "','"
                + apikey
                + "','"
                + sourceip
                + "','"
                + now
                + "','"
                + now
                + "','"
                + jsonstr
                + "');"
            )
        else:
            jsondata = json.loads(jsonstr)
            apikey = jsondata["api-key"]
            sourceip = jsondata["source-ip"]
            if istry:
                sql = (
                    "UPDATE requests SET try = "
                    + str(response["try"] + 1)
                    + ", status = '"
                    + status
                    + "', message = '"
                    + message
                    + "', last_date = '"
                    + now
                    + "', source_ip = '"
                    + sourceip
                    + "', api_key = '"
                    + apikey
                    + "'  where request_id = '"
                    + request_id
                    + "';"
                )
            elif decrement:
                sql = (
                    "UPDATE requests SET try = "
                    + str(response["try"] - 1)
                    + ", status = '"
                    + status
                    + "', message = '"
                    + message
                    + "', last_date = '"
                    + now
                    + "', source_ip = '"
                    + sourceip
                    + "', api_key = '"
                    + apikey
                    + "'  where request_id = '"
                    + request_id
                    + "';"
                )
            else:
                sql = (
                    "UPDATE requests SET status = '"
                    + status
                    + "', message = '"
                    + message
                    + "', last_date = '"
                    + now
                    + "' where request_id = '"
                    + request_id
                    + "';"
                )

        self.cursor().execute(sql)
        self.__db.commit()
