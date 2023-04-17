#!/usr/bin/env python3

from datetime import datetime, timedelta
from typing import Tuple

AVAILABLE_MET_MODELS = [
    "gfs",
    "nam",
    "hwrf",
    "hrrr",
    "hrrr-alaska",
    "nhc",
    "coamps",
    "wpc",
]


class Status:
    def __init__(self):
        pass

    @staticmethod
    def d2s(dt: datetime) -> str:
        if not dt:
            return None
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S")

    def get_status(self, status_type: str, limit: timedelta) -> Tuple[dict, int]:
        """
        This method is used to generate the status from the various sources
        """

        if status_type not in AVAILABLE_MET_MODELS:
            return {
                "message": "ERROR: Unknown model requested: '{:s}'".format(status_type)
            }, 400

        if status_type == "gfs":
            return self.__get_status_gfs(384, limit)
        elif status_type == "nam":
            return self.__get_status_nam(84, limit)
        elif status_type == "hwrf":
            return self.__get_status_hwrf(126, limit)
        elif status_type == "hrrr":
            return self.__get_status_hrrr(48, limit)
        elif status_type == "hrrr-alaksa":
            return self.__get_status_hrrr_alaska(48, limit)
        elif status_type == "wpc":
            return self.__get_status_wpc(162, limit)
        elif status_type == "nhc":
            return self.__get_status_nhc(limit)
        elif status_type == "coamps":
            return self.__get_status_coamps(limit)

    def __get_status_generic(
        self,
        met_source: str,
        table_type: any,
        cycle_duration: int,
        limit: timedelta,
    ) -> Tuple[dict, int]:
        from metget_api.database import Database

        db = Database()
        session = db.session()

        limit_time = datetime.utcnow() - limit
        unique_cycles = (
            session.query(table_type.forecastcycle)
            .distinct()
            .filter(table_type.forecastcycle >= limit_time)
            .order_by(table_type.forecastcycle.desc())
            .all()
        )

        if len(unique_cycles) == 0:
            return {
                "meteorological_source": met_source,
                "request_limit_days": limit.days,
                "min_forecast_date": None,
                "max_forecast_date": None,
                "first_available_cycle": None,
                "latest_available_cycle": None,
                "latest_available_cycle_length": None,
                "latest_complete_cycle": None,
                "complete_cycle_length": cycle_duration,
                "cycles_complete": None,
                "cycles": None,
            }, 200

        cycle_minimum = unique_cycles[-1][0]
        cycle_maximum = unique_cycles[0][0]

        complete_cycles = []
        incomplete_cycles = []
        cycle_list = []

        latest_complete = None
        latest_start = None
        latest_end = None
        latest_length = None
        min_forecast_time = None
        max_forecast_time = None
        latest_cycle_length = None
        latest_complete_cycle = None

        for cycle in unique_cycles:
            cycle_time = cycle[0]
            cycle_time_str = Status.d2s(cycle_time)

            forecast_times = (
                session.query(table_type.forecasttime)
                .filter(table_type.forecastcycle == cycle_time)
                .order_by(table_type.forecasttime)
                .all()
            )

            cycle_min = forecast_times[0][0]
            cycle_max = forecast_times[-1][0]
            dt = int((cycle_max - cycle_min).total_seconds() / 3600.0)

            if cycle[0] == cycle_maximum:
                latest_cycle_length = dt

            if dt >= cycle_duration:
                if not latest_complete_cycle:
                    latest_complete_cycle = cycle_time

            if min_forecast_time:
                min_forecast_time = min(cycle_min, min_forecast_time)
            else:
                min_forecast_time = cycle_min

            if max_forecast_time:
                max_forecast_time = max(cycle_max, max_forecast_time)
            else:
                max_forecast_time = cycle_max

            if dt >= cycle_duration:
                complete_cycles.append(cycle_time_str)
            else:
                incomplete_cycles.append(cycle_time_str)

            cycle_list.append({"cycle": cycle_time_str, "duration": dt})

        return {
            "meteorological_source": met_source,
            "request_limit_days": limit.days,
            "min_forecast_date": Status.d2s(min_forecast_time),
            "max_forecast_date": Status.d2s(max_forecast_time),
            "first_available_cycle": Status.d2s(cycle_minimum),
            "latest_available_cycle": Status.d2s(cycle_maximum),
            "latest_available_cycle_length": latest_cycle_length,
            "latest_complete_cycle": Status.d2s(latest_complete_cycle),
            "complete_cycle_length": cycle_duration,
            "cycles_complete": complete_cycles,
            "cycles": cycle_list,
        }, 200

    def __get_status_gfs(self, cycle_length: int, limit: timedelta) -> Tuple[dict, int]:
        from metget_api.tables import GfsTable

        return self.__get_status_generic("gfs", GfsTable, cycle_length, limit)

    def __get_status_nam(self, cycle_length: int, limit: timedelta) -> Tuple[dict, int]:
        from metget_api.tables import NamTable

        return self.__get_status_generic("nam", NamTable, cycle_length, limit)

    def __get_status_hrrr(
        self, cycle_length: int, limit: timedelta
    ) -> Tuple[dict, int]:
        from metget_api.tables import HrrrTable

        return self.__get_status_generic("hrrr", HrrrTable, cycle_length, limit)

    def __get_status_hrrr_alaska(
        self, cycle_length: int, limit: timedelta
    ) -> Tuple[dict, int]:
        from metget_api.tables import HrrrAlaskaTable

        return self.__get_status_generic(
            "hrrr-alaska", HrrrAlaskaTable, cycle_length, limit
        )

    def __get_status_wpc(self, cycle_length: int, limit: timedelta) -> Tuple[dict, int]:
        from metget_api.tables import WpcTable

        return self.__get_status_generic("wpc", WpcTable, cycle_length, limit)

    def __get_status_hwrf(
        self, cycle_duration: int, limit: timedelta
    ) -> Tuple[dict, int]:
        from metget_api.database import Database
        from metget_api.tables import HwrfTable

        db = Database()
        session = db.session()

        limit_time = datetime.utcnow() - limit
        unique_storms = (
            session.query(HwrfTable.stormname)
            .distinct()
            .filter(HwrfTable.forecastcycle >= limit_time)
            .all()
        )

        storms = {}

        for storm in unique_storms:
            storm_name = storm[0]
            unique_cycles = (
                session.query(HwrfTable.forecastcycle)
                .distinct()
                .filter(
                    HwrfTable.stormname == storm_name,
                    HwrfTable.forecastcycle >= limit_time,
                )
                .order_by(HwrfTable.forecastcycle)
                .all()
            )

            this_storm = {}
            this_storm_min_time = None
            this_storm_max_time = None
            this_storm_first_cycle = unique_cycles[0][0]
            this_storm_latest_cycle = unique_cycles[-1][0]
            this_storm_cycles = []
            this_storm_complete_cycles = []

            for cycle in unique_cycles:
                cycle_time = cycle[0]
                cycle_time_str = Status.d2s(cycle_time)
                forecast_times = (
                    session.query(HwrfTable.forecasttime)
                    .filter(
                        HwrfTable.stormname == storm_name,
                        HwrfTable.forecastcycle == cycle_time,
                    )
                    .order_by(HwrfTable.forecasttime)
                    .all()
                )
                min_time = forecast_times[0][0]
                max_time = forecast_times[-1][0]
                dt = int((max_time - min_time).total_seconds()/3600.0)

                if dt >= cycle_duration:
                    this_storm_complete_cycles.append(cycle_time_str)
                this_storm_cycles.append({"cycle": cycle_time_str, "duration": dt})
                
                if this_storm_min_time:
                    this_storm_min_time = min(this_storm_min_time, min_time)
                else:
                    this_storm_min_time = min_time

                if this_storm_max_time:
                    this_storm_max_time = max(this_storm_max_time, max_time)
                else:
                    this_storm_max_time = max_time

            this_storm["cycles"] = this_storm_cycles
            this_storm["complete_cycles"] = this_storm_complete_cycles
            this_storm["min_forecast_date"] = Status.d2s(this_storm_min_time)
            this_storm["max_forecast_date"] = Status.d2s(this_storm_max_time)
            this_storm["first_available_cycle"] = Status.d2s(this_storm_first_cycle)
            this_storm["latest_available_cycle"] = this_storm_cycles[-1]["cycle"]
            this_storm["lastest_available_cycle_length"] = this_storm_cycles[-1]["duration"]
            this_storm["latest_complete_cycle"] = this_storm_complete_cycles[-1]
            this_storm["complete_cycle_length"] = cycle_duration
            storms[storm_name] = this_storm

        return storms, 200

    def __get_status_coamps(self, limit: timedelta) -> Tuple[dict, int]:
        return {}, 200 

    def __get_status_nhc(self, limit: timedelta) -> Tuple[dict, int]:
        return {}, 200
