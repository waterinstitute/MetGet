from sqlalchemy import func
from datetime import datetime
from typing import Union
from metbuild.tables import TableBase
from metbuild.database import Database


class Filelist:
    """
    This class is used to generate a list of files that will be used to generate the
    requested forcing data.
    """

    def __init__(
        self,
        service: str,
        param: str,
        start: datetime,
        end: datetime,
        tau: int,
        storm_year: int,
        storm: int,
        basin: str,
        advisory: int,
        nowcast: bool,
        multiple_forecasts: bool,
        ensemble_member: str,
    ):
        """
        Constructor for the Filelist class

        Args:
            service (str): The service that is being requested
            param (str): The parameter that is being requested
            start (datetime): The start date of the request
            end (datetime): The end date of the request
            tau (int): The forecast lead time
            storm_year(int): The year of the storm
            storm (int): The storm number
            basin (str): The basin of the storm
            advisory (int): The advisory number
            nowcast (bool): Whether this is a nowcast
            multiple_forecasts (bool): Whether multiple forecasts are being requested
            ensemble_member (str): The ensemble member that is being requested

        """
        self.__service = service
        self.__param = param
        self.__start = start
        self.__end = end
        self.__tau = tau
        self.__storm_year = storm_year
        self.__storm = storm
        self.__basin = basin
        self.__advisory = advisory
        self.__nowcast = nowcast
        self.__multiple_forecasts = multiple_forecasts
        self.__ensemble_member = ensemble_member
        self.__error = []
        self.__valid = False
        self.__files = self.__query_files()

    @staticmethod
    def __rows2dicts(data: list) -> list:
        """
        This method is used to convert a list of rows to a list of dictionaries

        Args:
            data (list): The rows to convert

        """
        d = []
        for row in data:
            d.append(row._mapping)
        return d

    @staticmethod
    def __result_contains_time(data: list, key: str, time: datetime) -> bool:
        """
        This method is used to check if a list of dictionaries contains a specific
        time

        Args:
            data (list): The list of dictionaries to check
            key (str): The key to check
            time (datetime): The time to check for

        Returns:
            bool: True if the time is found, False otherwise
        """
        for row in data:
            if row[key] == time:
                return True
        return False

    @staticmethod
    def __merge_tau_excluded_data(data_single: list, data_tau: list) -> list:
        """
        This method is used to merge the data from the single forecast time query
        with the data from the tau excluded query

        Args:
            data_single (list): The data from the single forecast time query
            data_tau (list): The data from the tau excluded query

        Returns:
            list: The merged data
        """
        for row in data_tau:
            if not Filelist.__result_contains_time(
                data_single, "forecasttime", row["forecasttime"]
            ):
                data_single.append(row)

        data_single = sorted(data_single, key=lambda k: k["forecasttime"])

        return data_single

    def __query_files(self) -> Union[list, dict, None]:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        import sys

        self.__valid = True
        if self.__service == "gfs-ncep":
            return self.__query_files_gfs_ncep()
        elif self.__service == "nam-ncep":
            return self.__query_files_nam_ncep()
        elif self.__service == "hwrf":
            return self.__query_files_hwrf()
        elif self.__service == "coamps-tc":
            return self.__query_files_coamps_tc()
        elif self.__service == "hrrr-conus":
            return self.__query_files_hrrr_conus()
        elif self.__service == "hrrr-alaska":
            return self.__query_files_hrrr_alaska()
        elif self.__service == "gefs-ncep":
            return self.__query_files_gefs_ncep()
        elif self.__service == "wpc-ncep":
            return self.__query_files_wpc_ncep()
        elif self.__service == "nhc":
            return self.__query_files_nhc()
        else:
            self.__error.append("Invalid service: '{:s}'".format(self.__service))
            self.__valid = False
            return None

    def files(self) -> list:
        """
        This method is used to return the list of files that will be used to generate
        the requested forcing data

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        return self.__files

    def __query_generic_file_list(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for "generic" services that
        do not have a specific query method, such as GFS-NCEP, NAM-NCEP, HRRR, etc.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        if self.__nowcast:
            return self.__query_generic_file_list_nowcast(table)
        else:
            if self.__multiple_forecasts:
                return self.__query_generic_file_list_multiple_forecasts(table)
            else:
                return self.__query_generic_file_list_single_forecast(table)

    def __query_generic_file_list_nowcast(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for "generic" services that
        do not have a specific query method, such as GFS-NCEP, NAM-NCEP, HRRR, etc.
        This method is used for nowcasts, i.e. tau = 0

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        with Database() as db, db.session() as session:
            t2 = (
                session.query(table.forecasttime, func.max(table.index).label("id"))
                .filter(table.tau == 0)
                .group_by(table.forecasttime)
                .order_by(table.forecasttime)
                .subquery()
            )
            return Filelist.__rows2dicts(
                session.query(
                    table.index,
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .join(t2, table.index == t2.c.id)
                .filter(
                    table.index == t2.c.id,
                    table.tau == 0,
                    table.forecasttime == t2.c.forecasttime,
                    table.forecasttime >= self.__start,
                    table.forecasttime <= self.__end,
                )
                .order_by(table.forecasttime)
                .all()
            )

    def __query_generic_file_list_single_forecast(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for "generic" services that
        do not have a specific query method, such as GFS-NCEP, NAM-NCEP, HRRR, etc.
        This method is used for single forecast times, i.e. where forecastcycle is
        constant. The only exception is when tau is greater than 0, in which case
        the forecastcycle is allowed to vary during the tau period.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing

        """
        with Database() as db, db.session() as session:
            t2 = (
                session.query(table.forecasttime, func.max(table.index).label("id"))
                .group_by(table.forecasttime)
                .order_by(table.forecasttime)
                .subquery()
            )
            first_cycle = (
                session.query(
                    table.index,
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .join(t2, table.index == t2.c.id)
                .filter(
                    table.index == t2.c.id,
                    table.forecasttime == t2.c.forecasttime,
                    table.forecastcycle >= self.__start,
                    table.forecastcycle <= self.__end,
                )
                .order_by(table.forecastcycle)
                .first()
            )

            pure_forecast = Filelist.__rows2dicts(
                session.query(
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .filter(
                    table.forecastcycle == first_cycle[1],
                    table.tau >= self.__tau,
                    table.forecasttime >= self.__start,
                    table.forecasttime <= self.__end,
                )
                .order_by(table.forecasttime)
                .all()
            )

        # If tau is 0, we don't need to query the fallback data
        if self.__tau == 0:
            return pure_forecast
        else:
            # Query the fallback data to fill in when we select out the tau
            # forecasts
            fallback_data = Filelist.__rows2dicts(
                self.__query_generic_file_list_multiple_forecasts(table)
            )
            return Filelist.__merge_tau_excluded_data(pure_forecast, fallback_data)

    def __query_generic_file_list_multiple_forecasts(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for "generic" services that
        do not have a specific query method, such as GFS-NCEP, NAM-NCEP, HRRR, etc.
        This method is used to assemble data from multiple forecast cycles, i.e.
        where forecastcycle is not constant.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing

        """
        with Database() as db, db.session() as session:
            t2 = (
                session.query(table.forecasttime, func.max(table.index).label("id"))
                .filter(table.tau >= self.__tau)
                .group_by(table.forecasttime)
                .order_by(table.forecasttime)
                .subquery()
            )
            return Filelist.__rows2dicts(
                session.query(
                    table.index,
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .join(t2, table.index == t2.c.id)
                .filter(
                    table.index == t2.c.id,
                    table.tau >= self.__tau,
                    table.forecasttime == t2.c.forecasttime,
                    table.forecasttime >= self.__start,
                    table.forecasttime <= self.__end,
                )
                .order_by(table.forecasttime)
                .all()
            )

    def __query_files_gfs_ncep(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for GFS-NCEP.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import GfsTable

        return self.__query_generic_file_list(GfsTable)
    
    def __query_files_wpc_ncep(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for WPC-NCEP.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import WpcTable

        #...Skipping the zero hour for wpc rainfall
        #if self.__tau == 0:
        #    self.__tau == 1

        return self.__query_generic_file_list(WpcTable)

    def __query_files_nam_ncep(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for NAM-NCEP.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import NamTable

        return self.__query_generic_file_list(NamTable)

    def __query_files_hrrr_conus(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for HRRR.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import HrrrTable

        return self.__query_generic_file_list(HrrrTable)

    def __query_files_hrrr_alaska(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for HRRR-Alaska.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import HrrrAlaskaTable

        return self.__query_generic_file_list(HrrrAlaskaTable)

    def __query_files_gefs_ncep(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for GEFS-NCEP.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        if self.__nowcast:
            return self.__query_gefs_file_list_nowcast()
        else:
            if self.__multiple_forecasts:
                return self.__query_gefs_file_list_multiple_forecasts()
            else:
                return self.__query_gefs_file_list_single_forecast()

    def __query_gefs_file_list_single_forecast(self):
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for GEFS-NCEP. This method
        is used to assemble data from a single forecast cycle, i.e. where
        forecastcycle is constant.

        Returns:
            list: The list of files that will be used to generate the requested forcing

        """

        from .tables import GefsTable

        with Database() as db, db.session() as session:
            t2 = (
                session.query(
                    GefsTable.forecasttime, func.max(GefsTable.index).label("id")
                )
                .filter(GefsTable.ensemble_member == self.__ensemble_member)
                .group_by(GefsTable.forecasttime)
                .order_by(GefsTable.forecasttime)
                .subquery()
            )
            first_cycle = (
                session.query(
                    GefsTable.index,
                    GefsTable.forecastcycle,
                    GefsTable.forecasttime,
                    GefsTable.filepath,
                    GefsTable.tau,
                )
                .join(t2, GefsTable.index == t2.c.id)
                .filter(
                    GefsTable.index == t2.c.id,
                    GefsTable.forecasttime == t2.c.forecasttime,
                    GefsTable.forecastcycle >= self.__start,
                    GefsTable.forecastcycle <= self.__end,
                )
                .order_by(GefsTable.forecastcycle)
                .first()
            )

            pure_forecast = Filelist.__rows2dicts(
                session.query(
                    GefsTable.forecastcycle,
                    GefsTable.forecasttime,
                    GefsTable.filepath,
                    GefsTable.tau,
                )
                .filter(
                    GefsTable.forecastcycle == first_cycle[1],
                    GefsTable.tau >= self.__tau,
                    GefsTable.ensemble_member == self.__ensemble_member,
                    GefsTable.forecasttime >= self.__start,
                    GefsTable.forecasttime <= self.__end,
                )
                .order_by(GefsTable.forecasttime)
                .all()
            )

        # If tau is 0, we don't need to query the fallback data
        if self.__tau == 0:
            return pure_forecast
        else:
            # Query the fallback data to fill in when we select out the tau
            # forecasts
            fallback_data = Filelist.__rows2dicts(
                self.__query_gefs_file_list_multiple_forecasts()
            )
            return Filelist.__merge_tau_excluded_data(pure_forecast, fallback_data)

    def __query_gefs_file_list_multiple_forecasts(self):
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for GEFS-NCEP. This method is used to
        assemble data from multiple forecast cycles, i.e. where forecastcycle is not constant.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import GefsTable

        with Database() as db, db.session() as session:
            t2 = (
                session.query(
                    GefsTable.forecasttime, func.max(GefsTable.index).label("id")
                )
                .filter(
                    GefsTable.tau >= self.__tau,
                    GefsTable.ensemble_member == self.__ensemble_member,
                )
                .group_by(GefsTable.forecasttime)
                .order_by(GefsTable.forecasttime)
                .subquery()
            )
            return Filelist.__rows2dicts(
                session.query(
                    GefsTable.index,
                    GefsTable.forecastcycle,
                    GefsTable.forecasttime,
                    GefsTable.filepath,
                    GefsTable.tau,
                )
                .join(t2, GefsTable.index == t2.c.id)
                .filter(
                    GefsTable.index == t2.c.id,
                    GefsTable.tau >= self.__tau,
                    GefsTable.forecasttime == t2.c.forecasttime,
                    GefsTable.forecasttime >= self.__start,
                    GefsTable.forecasttime <= self.__end,
                )
                .order_by(GefsTable.forecasttime)
                .all()
            )

    def __query_gefs_file_list_nowcast(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for GEFS-NCEP nowcasts.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import GefsTable

        with Database() as db, db.session() as session:
            t2 = (
                session.query(
                    GefsTable.forecasttime, func.max(GefsTable.index).label("id")
                )
                .filter(
                    GefsTable.tau == 0,
                    GefsTable.ensemble_member == self.__ensemble_member,
                )
                .group_by(GefsTable.forecasttime)
                .order_by(GefsTable.forecasttime)
                .subquery()
            )

            return Filelist.__rows2dicts(
                session.query(
                    GefsTable.index,
                    GefsTable.forecastcycle,
                    GefsTable.forecasttime,
                    GefsTable.filepath,
                    GefsTable.tau,
                )
                .join(t2, GefsTable.index == t2.c.id)
                .filter(
                    GefsTable.index == t2.c.id,
                    GefsTable.tau == 0,
                    GefsTable.forecasttime == t2.c.forecasttime,
                    GefsTable.forecasttime >= self.__start,
                    GefsTable.forecasttime <= self.__end,
                )
                .order_by(GefsTable.forecasttime)
                .all()
            )

    def __query_files_hwrf(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for HWRF.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import HwrfTable

        return self.__query_storm_file_list(HwrfTable)

    def __query_files_coamps_tc(self) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for COAMPS.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import CoampsTable

        return self.__query_storm_file_list(CoampsTable)

    def __query_storm_file_list(self, table: TableBase):
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for meteorology which supports
        named storms.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """

        if self.__nowcast:
            return self.__query_storm_file_list_nowcast(table)
        else:
            if self.__multiple_forecasts:
                return self.__query_storm_file_list_multiple_forecasts(table)
            else:
                return self.__query_storm_file_list_single_forecast(table)

    def __query_storm_file_list_single_forecast(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for meteorology which supports
        named storms. This method is used to assemble data from a single forecast cycle,
        i.e. where forecastcycle is constant.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing

        """

        with Database() as db, db.session() as session:
            t2 = (
                session.query(table.forecasttime, func.max(table.index).label("id"))
                .filter(table.stormname == self.__storm)
                .group_by(table.forecasttime)
                .order_by(table.forecasttime)
                .subquery()
            )
            first_cycle = (
                session.query(
                    table.index,
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .join(t2, table.index == t2.c.id)
                .filter(
                    table.index == t2.c.id,
                    table.forecasttime == t2.c.forecasttime,
                    table.forecastcycle >= self.__start,
                    table.forecastcycle <= self.__end,
                )
                .order_by(table.forecastcycle)
                .first()
            )

            pure_forecast = Filelist.__rows2dicts(
                session.query(
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .filter(
                    table.forecastcycle == first_cycle[1],
                    table.tau >= self.__tau,
                    table.stormname == self.__storm,
                    table.forecasttime >= self.__start,
                    table.forecasttime <= self.__end,
                )
                .order_by(table.forecasttime)
                .all()
            )

        # If tau is 0, we don't need to query the fallback data
        if self.__tau == 0:
            return pure_forecast
        else:
            # Query the fallback data to fill in when we select out the tau
            # forecasts
            fallback_data = Filelist.__rows2dicts(
                self.__query_storm_file_list_multiple_forecasts(table)
            )
            return Filelist.__merge_tau_excluded_data(pure_forecast, fallback_data)

    def __query_storm_file_list_multiple_forecasts(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for meteorology which supports
        named storms. This method is used to assemble data from multiple forecast
        cycles, i.e. where forecastcycle is not constant.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """

        with Database() as db, db.session() as session:
            t2 = (
                session.query(table.forecasttime, func.max(table.index).label("id"))
                .filter(
                    table.tau >= self.__tau,
                    table.stormname == self.__storm,
                )
                .group_by(table.forecasttime)
                .order_by(table.forecasttime)
                .subquery()
            )
            return Filelist.__rows2dicts(
                session.query(
                    table.index,
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .join(t2, table.index == t2.c.id)
                .filter(
                    table.index == t2.c.id,
                    table.tau >= self.__tau,
                    table.forecasttime == t2.c.forecasttime,
                    table.forecasttime >= self.__start,
                    table.forecasttime <= self.__end,
                )
                .order_by(table.forecasttime)
                .all()
            )

    def __query_storm_file_list_nowcast(self, table: TableBase) -> list:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used for meteorology which supports
        named storms. This method is used to assemble data from multiple forecast
        cycles, i.e. where forecastcycle is not constant.

        Args:
            table (TableBase): The table to query

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """

        with Database() as db, db.session() as session:
            t2 = (
                session.query(table.forecasttime, func.max(table.index).label("id"))
                .filter(table.tau == 0, table.stormname == self.__storm)
                .group_by(table.forecasttime)
                .order_by(table.forecasttime)
                .subquery()
            )

            return Filelist.__rows2dicts(
                session.query(
                    table.index,
                    table.forecastcycle,
                    table.forecasttime,
                    table.filepath,
                    table.tau,
                )
                .join(t2, table.index == t2.c.id)
                .filter(
                    table.index == t2.c.id,
                    table.tau == 0,
                    table.forecasttime == t2.c.forecasttime,
                    table.forecasttime >= self.__start,
                    table.forecasttime <= self.__end,
                )
                .order_by(table.forecasttime)
                .all()
            )

    def __query_files_nhc(self) -> Union[dict, None]:
        """
        This method is used to query the database for the files that will be used to
        generate the requested forcing data. It is used to return the advisory and
        best track files for nhc storms.

        Returns:
            list: The list of files that will be used to generate the requested forcing
        """
        from .tables import NhcBtkTable, NhcFcstTable

        with Database() as db, db.session() as session:
            best_track_query = (
                session.query(NhcBtkTable)
                .filter(
                    NhcBtkTable.storm_year == self.__storm_year,
                    NhcBtkTable.basin == self.__basin,
                    NhcBtkTable.storm == self.__storm,
                )
                .all()
            )

            if len(best_track_query) == 0:
                best_track = None
            else:
                best_track = {
                    "start": best_track_query[0].advisory_start,
                    "end": best_track_query[0].advisory_end,
                    "duration": best_track_query[0].advisory_duration_hr,
                    "filepath": best_track_query[0].filepath,
                }

            forecast_track_query = (
                session.query(NhcFcstTable)
                .filter(
                    NhcFcstTable.storm_year == self.__storm_year,
                    NhcFcstTable.basin == self.__basin,
                    NhcFcstTable.storm == self.__storm,
                    NhcFcstTable.advisory == self.__advisory,
                )
                .all()
            )

        if len(forecast_track_query) == 0:
            forecast_track = None
        else:
            forecast_track = {
                "start": forecast_track_query[0].advisory_start,
                "end": forecast_track_query[0].advisory_end,
                "duration": forecast_track_query[0].advisory_duration_hr,
                "filepath": forecast_track_query[0].filepath,
            }

        if not best_track and not forecast_track:
            return None
        else:
            return {"best_track": best_track, "forecast_track": forecast_track}
