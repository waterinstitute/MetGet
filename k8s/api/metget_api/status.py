#!/usr/bin/env python3

from datetime import datetime, timedelta
from typing import Tuple, Union

AVAILABLE_MET_MODELS = [
    "gfs",
    "gefs",
    "nam",
    "hwrf",
    "hrrr",
    "hrrr-alaska",
    "nhc",
    "coamps",
    "ctcx",
    "wpc",
]

MET_MODEL_FORECAST_DURATION = {
    "gfs": 384,
    "gefs": 240,
    "nam": 84,
    "hwrf": 126,
    "hrrr": 48,
    "hrrr-alaska": 48,
    "coamps": 126,
    "wpc": 162,
}


class Status:
    """
    This class is used to generate the status of the various models in the database
    for the user. The status is returned as a dictionary which is converted to JSON
    by the api
    """

    def __init__(self):
        pass

    @staticmethod
    def d2s(dt: datetime) -> Union[str, None]:
        """
        This method is used to convert a datetime object to a string so that it can
        be returned to the user in the JSON response

        Args:
            dt: Datetime object to convert to a string

        Returns:
            String representation of the datetime object

        """
        if not dt:
            return None
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_status(request) -> Tuple[dict, int]:
        """
        This method is used to generate the status from the various sources

        The types of status values that are valid are:
            - gfs
            - nam
            - hwrf
            - hrrr
            - hrrr-alaska
            - wpc
            - nhc
            - coamps

        Args:
            request: A flask request object

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from datetime import timedelta

        if "model" in request.args:
            status_type = request.args["model"]
        else:
            status_type = "all"

        if "storm" in request.args:
            storm = request.args["storm"]
        else:
            storm = "all"

        if "member" in request.args:
            member = request.args["member"]
        else:
            member = "all"

        if "limit" in request.args:
            limit_days = request.args["limit"]
            try:
                limit_days_int = int(limit_days)
            except ValueError:
                return {
                    "statusCode": 400,
                    "body": {"message": "ERROR: Invalid limit specified"},
                }, 400
            time_limit = timedelta(days=limit_days_int)
            start_dt = None
            end_dt = None
        elif "start" in request.args and "end" in request.args:
            start = request.args["start"]
            end = request.args["end"]
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                return {
                    "statusCode": 400,
                    "body": {"message": "ERROR: Invalid start/end specified"},
                }, 400
            time_limit = None
        else:
            limit_days_int = 3
            time_limit = timedelta(days=limit_days_int)
            start_dt = None
            end_dt = None

        s = None

        if status_type not in AVAILABLE_MET_MODELS and status_type != "all":
            return {
                "message": "ERROR: Unknown model requested: '{:s}'".format(status_type)
            }, 400

        if status_type == "gfs":
            s = Status.__get_status_gfs(
                MET_MODEL_FORECAST_DURATION["gfs"], time_limit, start_dt, end_dt
            )
        elif status_type == "gefs":
            s = Status.__get_status_gefs(
                MET_MODEL_FORECAST_DURATION["gefs"],
                time_limit,
                start_dt,
                end_dt,
                member,
            )
        elif status_type == "nam":
            s = Status.__get_status_nam(
                MET_MODEL_FORECAST_DURATION["nam"], time_limit, start_dt, end_dt
            )
        elif status_type == "hwrf":
            s = Status.__get_status_hwrf(
                MET_MODEL_FORECAST_DURATION["hwrf"],
                time_limit,
                start_dt,
                end_dt,
                storm,
            )
        elif status_type == "hrrr":
            s = Status.__get_status_hrrr(
                MET_MODEL_FORECAST_DURATION["hrrr"],
                time_limit,
                start_dt,
                end_dt,
            )
        elif status_type == "hrrr-alaska":
            s = Status.__get_status_hrrr_alaska(
                MET_MODEL_FORECAST_DURATION["hrrr-alaska"], time_limit, start_dt, end_dt
            )
        elif status_type == "wpc":
            s = Status.__get_status_wpc(
                MET_MODEL_FORECAST_DURATION["wpc"], time_limit, start_dt, end_dt
            )
        elif status_type == "nhc":
            s = Status.__get_status_nhc(time_limit, start_dt, end_dt)
        elif status_type == "coamps":
            s = Status.__get_status_coamps(
                MET_MODEL_FORECAST_DURATION["coamps"],
                time_limit,
                start_dt,
                end_dt,
                storm,
            )
        elif status_type == "ctcx":
            s = Status.__get_status_ctcx(
                MET_MODEL_FORECAST_DURATION["coamps"],
                time_limit,
                start_dt,
                end_dt,
                storm,
                member,
            )
        elif status_type == "all":
            gfs, _ = Status.__get_status_gfs(
                MET_MODEL_FORECAST_DURATION["gfs"], time_limit, start_dt, end_dt
            )
            gefs, _ = Status.__get_status_gefs(
                MET_MODEL_FORECAST_DURATION["gefs"],
                time_limit,
                start_dt,
                end_dt,
                member,
            )
            nam, _ = Status.__get_status_nam(
                MET_MODEL_FORECAST_DURATION["nam"], time_limit, start_dt, end_dt
            )
            hwrf, _ = Status.__get_status_hwrf(
                MET_MODEL_FORECAST_DURATION["hwrf"],
                time_limit,
                start_dt,
                end_dt,
                storm,
            )
            hrrr, _ = Status.__get_status_hrrr(
                MET_MODEL_FORECAST_DURATION["hrrr"], time_limit, start_dt, end_dt
            )
            hrrr_alaska, _ = Status.__get_status_hrrr_alaska(
                MET_MODEL_FORECAST_DURATION["hrrr-alaska"], time_limit, start_dt, end_dt
            )
            nhc, _ = Status.__get_status_nhc(time_limit, start_dt, end_dt)
            wpc, _ = Status.__get_status_wpc(
                MET_MODEL_FORECAST_DURATION["wpc"], time_limit, start_dt, end_dt
            )
            coamps, _ = Status.__get_status_coamps(
                MET_MODEL_FORECAST_DURATION["coamps"],
                time_limit,
                start_dt,
                end_dt,
                storm,
            )
            ctcx, _ = Status.__get_status_ctcx(
                MET_MODEL_FORECAST_DURATION["coamps"],
                time_limit,
                start_dt,
                end_dt,
                storm,
                member,
            )
            s = {
                "gfs": gfs,
                "gefs": gefs,
                "nam": nam,
                "hwrf": hwrf,
                "hrrr": hrrr,
                "hrrr-alaska": hrrr_alaska,
                "nhc": nhc,
                "wpc": wpc,
                "coamps": coamps,
                "ctcx": ctcx,
            }

        return s, 200

    @staticmethod
    def __get_status_generic(
        met_source: str,
        table_type: any,
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
    ) -> dict:
        """
        This method is used to generate the status for the generic models (i.e. GFS, NAM, WPC, etc.)

        Args:
            met_source: The name of the meteorological source
            table_type: The table type to use when querying the database
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.database import Database

        time_limits = Status.__compute_time_limits(limit, start, end)

        with Database() as db, db.session() as session:
            unique_cycles = (
                session.query(table_type.forecastcycle)
                .distinct()
                .filter(table_type.forecastcycle >= time_limits["start"])
                .filter(table_type.forecastcycle <= time_limits["end"])
                .order_by(table_type.forecastcycle.desc())
                .all()
            )

        if len(unique_cycles) == 0:
            return {
                "meteorological_source": met_source,
                "request_limit_days": time_limits["days"],
                "request_limit_start": time_limits["start_str"],
                "request_limit_end": time_limits["end_str"],
                "min_forecast_date": None,
                "max_forecast_date": None,
                "first_available_cycle": None,
                "latest_available_cycle": None,
                "latest_available_cycle_length": None,
                "latest_complete_cycle": None,
                "complete_cycle_length": cycle_duration,
                "cycles_complete": None,
                "cycles": None,
            }

        cycle_minimum = unique_cycles[-1][0]
        cycle_maximum = unique_cycles[0][0]

        complete_cycles = []
        cycle_list = []

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

            cycle_list.append({"cycle": cycle_time_str, "duration": dt})

        return {
            "meteorological_source": met_source,
            "request_limit_days": time_limits["days"],
            "request_limit_start": time_limits["start_str"],
            "request_limit_end": time_limits["end_str"],
            "min_forecast_date": Status.d2s(min_forecast_time),
            "max_forecast_date": Status.d2s(max_forecast_time),
            "first_available_cycle": Status.d2s(cycle_minimum),
            "latest_available_cycle": Status.d2s(cycle_maximum),
            "latest_available_cycle_length": latest_cycle_length,
            "latest_complete_cycle": Status.d2s(latest_complete_cycle),
            "complete_cycle_length": cycle_duration,
            "cycles_complete": complete_cycles,
            "cycles": cycle_list,
        }

    @staticmethod
    def __compute_time_limits(
        limit: timedelta,
        start: datetime,
        end: datetime,
    ) -> dict:
        """
        This method is used to compute the time limits for the status

        Args:
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Tuple containing the time limits
        """
        if limit is not None:
            limit_time = datetime.utcnow() - limit
            limit_days = limit.days
            start = limit_time
            end = datetime.utcnow()
            limit_start_str = Status.d2s(limit_time)
            limit_end_str = Status.d2s(datetime.utcnow())
            method = "limit"
        elif start is not None and end is not None:
            limit_days = (end - start).total_seconds() / 86400.0
            limit_start_str = Status.d2s(start)
            limit_end_str = Status.d2s(end)
            method = "startend"
        else:
            raise ValueError("ERROR: Invalid limit provided")

        return {
            "days": limit_days,
            "start": start,
            "start_str": limit_start_str,
            "end": end,
            "end_str": limit_end_str,
            "method": method,
        }

    @staticmethod
    def __get_status_generic_ensemble(
        table_type: any,
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        ensemble_member: str,
    ) -> dict:
        """
        This method is used to generate the status for the generic models which have ensemble members (i.e. GEFS)

        Args:
            table_type: The table type to use when querying the database
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status
            ensemble_member: The ensemble member to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.database import Database

        time_limits = Status.__compute_time_limits(limit, start, end)

        with Database() as db, db.session() as session:
            if ensemble_member == "all":
                unique_members = (
                    session.query(table_type.ensemble_member)
                    .distinct()
                    .filter(
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                    )
                    .all()
                )
            else:
                unique_members = (
                    session.query(table_type.ensemble_member)
                    .distinct()
                    .filter(
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                        table_type.ensemble_member == ensemble_member,
                    )
                    .all()
                )

            if len(unique_members) == 0:
                return {}

            members = {}

            for member in unique_members:

                member_name = member[0]

                unique_cycles = (
                    session.query(table_type.forecastcycle)
                    .distinct()
                    .filter(
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                        table_type.ensemble_member == member[0],
                    )
                    .order_by(table_type.forecastcycle.desc())
                    .all()
                )

                if len(unique_cycles) == 0:
                    members[member_name] = {
                        "request_limit_days": time_limits["days"],
                        "request_limit_start": time_limits["start_str"],
                        "request_limit_end": time_limits["end_str"],
                        "min_forecast_date": None,
                        "max_forecast_date": None,
                        "first_available_cycle": None,
                        "latest_available_cycle": None,
                        "latest_available_cycle_length": None,
                        "latest_complete_cycle": None,
                        "complete_cycle_length": cycle_duration,
                        "cycles_complete": None,
                        "cycles": None,
                    }
                    continue

                cycle_minimum = unique_cycles[-1][0]
                cycle_maximum = unique_cycles[0][0]

                complete_cycles = []
                cycle_list = []

                min_forecast_time = None
                max_forecast_time = None
                latest_cycle_length = None
                latest_complete_cycle = None

                for cycle in unique_cycles:
                    cycle_time = cycle[0]
                    cycle_time_str = Status.d2s(cycle_time)

                    forecast_times = (
                        session.query(table_type.forecasttime)
                        .filter(
                            table_type.forecastcycle == cycle_time,
                            table_type.ensemble_member == member[0],
                        )
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

                    cycle_list.append({"cycle": cycle_time_str, "duration": dt})

                members[member_name] = {
                    "request_limit_days": time_limits["days"],
                    "request_limit_start": time_limits["start_str"],
                    "request_limit_end": time_limits["end_str"],
                    "min_forecast_date": Status.d2s(min_forecast_time),
                    "max_forecast_date": Status.d2s(max_forecast_time),
                    "first_available_cycle": Status.d2s(cycle_minimum),
                    "latest_available_cycle": Status.d2s(cycle_maximum),
                    "latest_available_cycle_length": latest_cycle_length,
                    "latest_complete_cycle": Status.d2s(latest_complete_cycle),
                    "complete_cycle_length": cycle_duration,
                    "cycles_complete": complete_cycles,
                    "cycles": cycle_list,
                }

            return members

    @staticmethod
    def __get_status_gfs(
        cycle_length: int, limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        This method is used to generate the status for the GFS model

        Args:
            cycle_length: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import GfsTable

        return Status.__get_status_generic(
            "gfs", GfsTable, cycle_length, limit, start, end
        )

    @staticmethod
    def __get_status_gefs(
        cycle_length: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        member: str,
    ) -> dict:
        """
        This method is used to generate the status for the GEFS model

        Args:
            cycle_length: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status
            member: The ensemble member to use when generating the status
        """
        from metbuild.tables import GefsTable

        return Status.__get_status_generic_ensemble(
            GefsTable,
            cycle_length,
            limit,
            start,
            end,
            member,
        )

    @staticmethod
    def __get_status_nam(
        cycle_length: int, limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        This method is used to generate the status for the NAM model

        Args:
            cycle_length: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status


        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import NamTable

        return Status.__get_status_generic(
            "nam", NamTable, cycle_length, limit, start, end
        )

    @staticmethod
    def __get_status_hrrr(
        cycle_length: int, limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        This method is used to generate the status for the HRRR model

        Args:
            cycle_length: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import HrrrTable

        return Status.__get_status_generic(
            "hrrr", HrrrTable, cycle_length, limit, start, end
        )

    @staticmethod
    def __get_status_hrrr_alaska(
        cycle_length: int, limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        This method is used to generate the status for the HRRR Alaska model

        Args:
            cycle_length: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import HrrrAlaskaTable

        return Status.__get_status_generic(
            "hrrr-alaska", HrrrAlaskaTable, cycle_length, limit, start, end
        )

    @staticmethod
    def __get_status_wpc(
        cycle_length: int, limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        This method is used to generate the status for the WPC QPF data

        Args:
            cycle_length: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import WpcTable

        return Status.__get_status_generic(
            "wpc", WpcTable, cycle_length, limit, start, end
        )

    @staticmethod
    def __get_status_hwrf(
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        storm: str,
    ) -> dict:
        """
        This method is used to generate the status for the HWRF model

        Args:
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status
            storm: The storm to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import HwrfTable

        return Status.__get_status_deterministic_storm_type(
            HwrfTable,
            cycle_duration,
            limit,
            start,
            end,
            storm,
        )

    @staticmethod
    def __get_status_coamps(
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        storm: str,
    ) -> dict:
        """
        This method is used to generate the status for the COAMPS-TC model

        Args:
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status
            storm: The storm to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import CoampsTable

        return Status.__get_status_deterministic_storm_type(
            CoampsTable,
            cycle_duration,
            limit,
            start,
            end,
            storm,
        )

    @staticmethod
    def __get_status_ctcx(
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        storm: str,
        member: str,
    ) -> dict:
        """
        This method is used to generate the status for the CTCX model

        Args:
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status
            storm: The storm to use when generating the status
            member: The ensemble member to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.tables import CtcxTable

        return Status.__get_status_ensemble_storm_type(
            CtcxTable,
            cycle_duration,
            limit,
            start,
            end,
            storm,
            member,
        )

    @staticmethod
    def __get_status_ensemble_storm_type(
        table_type: any,
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        storm: str,
        ensemble_member: str,
    ) -> dict:
        """
        This method is used to generate the status for the deterministic storm type models
        such as COAMPS-CTCX

        Args:
            table_type: The table type to use when generating the status
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status
            storm: The storm to use when generating the status
            ensemble_member: The ensemble member to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.database import Database

        time_limits = Status.__compute_time_limits(limit, start, end)

        with Database() as db, db.session() as session:

            if storm == "all":
                unique_storms = (
                    session.query(table_type.stormname)
                    .distinct()
                    .filter(
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                    )
                    .all()
                )
            else:
                unique_storms = (
                    session.query(table_type.stormname)
                    .distinct()
                    .filter(
                        table_type.stormname == storm,
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                    )
                    .all()
                )

            storms = {}

            for storm in unique_storms:
                storm_name = storm[0]
                storms[storm_name] = {}

                if ensemble_member == "all":
                    unique_ensemble_members = (
                        session.query(table_type.ensemble_member)
                        .distinct()
                        .filter(
                            table_type.stormname == storm_name,
                            table_type.forecastcycle >= time_limits["start"],
                            table_type.forecastcycle <= time_limits["end"],
                        )
                        .order_by(table_type.ensemble_member)
                        .all()
                    )
                else:
                    unique_ensemble_members = (
                        session.query(table_type.ensemble_member)
                        .distinct()
                        .filter(
                            table_type.stormname == storm_name,
                            table_type.forecastcycle >= time_limits["start"],
                            table_type.forecastcycle <= time_limits["end"],
                            table_type.ensemble_member == ensemble_member,
                        )
                        .order_by(table_type.ensemble_member)
                        .all()
                    )

                for member in unique_ensemble_members:

                    member_name = member[0]

                    unique_cycles = (
                        session.query(table_type.forecastcycle)
                        .distinct()
                        .filter(
                            table_type.stormname == storm_name,
                            table_type.ensemble_member == member[0],
                            table_type.forecastcycle >= time_limits["start"],
                            table_type.forecastcycle <= time_limits["end"],
                        )
                        .order_by(table_type.forecastcycle)
                        .all()
                    )

                    this_member = {}
                    this_member_min_time = None
                    this_member_max_time = None
                    this_member_cycles = []
                    this_member_complete_cycles = []

                    for cycle in unique_cycles:
                        cycle_time = cycle[0]
                        cycle_time_str = Status.d2s(cycle_time)
                        forecast_times = (
                            session.query(table_type.forecasttime)
                            .filter(
                                table_type.stormname == storm_name,
                                table_type.forecastcycle == cycle_time,
                            )
                            .order_by(table_type.forecasttime)
                            .all()
                        )
                        min_time = forecast_times[0][0]
                        max_time = forecast_times[-1][0]
                        dt = int((max_time - min_time).total_seconds() / 3600.0)

                        if dt >= cycle_duration:
                            this_member_complete_cycles.append(cycle_time_str)
                        this_member_cycles.append(
                            {"cycle": cycle_time_str, "duration": dt}
                        )

                        if this_member_min_time:
                            this_member_min_time = min(this_member_min_time, min_time)
                        else:
                            this_member_min_time = min_time

                        if this_member_max_time:
                            this_member_max_time = max(this_member_max_time, max_time)
                        else:
                            this_member_max_time = max_time

                    this_member["min_forecast_date"] = Status.d2s(this_member_min_time)
                    this_member["max_forecast_date"] = Status.d2s(this_member_max_time)
                    this_member["first_available_cycle"] = this_member_cycles[0][
                        "cycle"
                    ]
                    this_member["latest_available_cycle"] = this_member_cycles[-1][
                        "cycle"
                    ]
                    this_member["latest_available_cycle_length"] = this_member_cycles[
                        -1
                    ]["duration"]
                    this_member["latest_complete_cycle"] = this_member_complete_cycles[
                        -1
                    ]
                    this_member["complete_cycle_length"] = cycle_duration

                    this_member_cycles.reverse()
                    this_member_complete_cycles.reverse()

                    this_member["cycles"] = this_member_cycles
                    this_member["cycles_complete"] = this_member_complete_cycles

                    storms[storm_name][member_name] = this_member

        return storms

    @staticmethod
    def __get_status_deterministic_storm_type(
        table_type: any,
        cycle_duration: int,
        limit: timedelta,
        start: datetime,
        end: datetime,
        storm: str,
    ) -> dict:
        """
        This method is used to generate the status for the deterministic storm type models
        such as HWRF and COAMPS-TC

        Args:
            table_type: The table type to use when generating the status
            cycle_duration: The duration of the cycle in hours
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.database import Database

        time_limits = Status.__compute_time_limits(limit, start, end)

        with Database() as db, db.session() as session:

            if storm == "all":
                unique_storms = (
                    session.query(table_type.stormname)
                    .distinct()
                    .filter(
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                    )
                    .all()
                )
            else:
                unique_storms = (
                    session.query(table_type.stormname)
                    .distinct()
                    .filter(
                        table_type.stormname == storm,
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                    )
                    .all()
                )

            storms = {}

            for storm in unique_storms:
                storm_name = storm[0]

                unique_cycles = (
                    session.query(table_type.forecastcycle)
                    .distinct()
                    .filter(
                        table_type.stormname == storm_name,
                        table_type.forecastcycle >= time_limits["start"],
                        table_type.forecastcycle <= time_limits["end"],
                    )
                    .order_by(table_type.forecastcycle)
                    .all()
                )

                this_storm = {}
                this_storm_min_time = None
                this_storm_max_time = None
                this_storm_cycles = []
                this_storm_complete_cycles = []

                for cycle in unique_cycles:
                    cycle_time = cycle[0]
                    cycle_time_str = Status.d2s(cycle_time)
                    forecast_times = (
                        session.query(table_type.forecasttime)
                        .filter(
                            table_type.stormname == storm_name,
                            table_type.forecastcycle == cycle_time,
                        )
                        .order_by(table_type.forecasttime)
                        .all()
                    )
                    min_time = forecast_times[0][0]
                    max_time = forecast_times[-1][0]
                    dt = int((max_time - min_time).total_seconds() / 3600.0)

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

                this_storm["min_forecast_date"] = Status.d2s(this_storm_min_time)
                this_storm["max_forecast_date"] = Status.d2s(this_storm_max_time)
                this_storm["first_available_cycle"] = this_storm_cycles[0]["cycle"]
                this_storm["latest_available_cycle"] = this_storm_cycles[-1]["cycle"]
                this_storm["latest_available_cycle_length"] = this_storm_cycles[-1][
                    "duration"
                ]
                this_storm["latest_complete_cycle"] = this_storm_complete_cycles[-1]
                this_storm["complete_cycle_length"] = cycle_duration

                this_storm_cycles.reverse()
                this_storm_complete_cycles.reverse()

                this_storm["cycles"] = this_storm_cycles
                this_storm["cycles_complete"] = this_storm_complete_cycles

                storms[storm_name] = this_storm

        return storms

    @staticmethod
    def __get_status_nhc(limit: timedelta, start: datetime, end: datetime) -> dict:
        """
        This method is used to generate the status for the NHC model

        Args:
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        best_track = Status.__get_status_nhc_besttrack(limit, start, end)
        forecast = Status.__get_status_nhc_forecast(limit, start, end)
        return {"best_track": best_track, "forecast": forecast}

    @staticmethod
    def __get_status_nhc_besttrack(
        limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        This method is used to generate the status information for the
        NHC best track data

        Args:
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.database import Database
        from metbuild.tables import NhcBtkTable
        from sqlalchemy import or_, and_

        time_limits = Status.__compute_time_limits(limit, start, end)

        with Database() as db, db.session() as session:

            basins = (
                session.query(NhcBtkTable.basin)
                .distinct()
                .filter(
                    and_(
                        or_(
                            NhcBtkTable.advisory_start >= time_limits["start"],
                            NhcBtkTable.advisory_end >= time_limits["start"],
                        ),
                        or_(
                            NhcBtkTable.advisory_start <= time_limits["end"],
                            NhcBtkTable.advisory_end <= time_limits["end"],
                        ),
                    )
                )
                .all()
            )
            storm_years = (
                session.query(NhcBtkTable.storm_year)
                .distinct()
                .filter(
                    and_(
                        or_(
                            NhcBtkTable.advisory_start >= time_limits["start"],
                            NhcBtkTable.advisory_end >= time_limits["start"],
                        ),
                        or_(
                            NhcBtkTable.advisory_start <= time_limits["end"],
                            NhcBtkTable.advisory_end <= time_limits["end"],
                        ),
                    )
                )
                .all()
            )
            storms = (
                session.query(
                    NhcBtkTable.basin,
                    NhcBtkTable.storm_year,
                    NhcBtkTable.storm,
                    NhcBtkTable.advisory_start,
                    NhcBtkTable.advisory_end,
                    NhcBtkTable.advisory_duration_hr,
                )
                .filter(
                    and_(
                        or_(
                            NhcBtkTable.advisory_start >= time_limits["start"],
                            NhcBtkTable.advisory_end >= time_limits["start"],
                        ),
                        or_(
                            NhcBtkTable.advisory_start <= time_limits["end"],
                            NhcBtkTable.advisory_end <= time_limits["end"],
                        ),
                    )
                )
                .order_by(NhcBtkTable.basin, NhcBtkTable.storm)
                .all()
            )

            storm_data = {}
            for y in storm_years:
                storm_data[y[0]] = {}
                for b in basins:
                    storm_data[y[0]][b[0]] = {}

            for storm in storms:
                b = storm[0]
                y = storm[1]
                n = storm[2]
                start_btk = Status.d2s(storm[3])
                end_btk = Status.d2s(storm[4])
                duration = storm[5]
                storm_data[y][b][n] = {
                    "best_track_start": start_btk,
                    "best_track_end": end_btk,
                    "duration": duration,
                }

        return storm_data

    @staticmethod
    def __get_status_nhc_forecast(
        limit: timedelta, start: datetime, end: datetime
    ) -> dict:
        """
        Method to generate the status data for NHC forecast data

        Args:
            limit: The limit in days to use when generating the status
            start: The start date to use when generating the status
            end: The end date to use when generating the status

        Returns:
            Dictionary containing the status information and the HTTP status code
        """
        from metbuild.database import Database
        from metbuild.tables import NhcFcstTable
        from sqlalchemy import or_, and_

        time_limits = Status.__compute_time_limits(limit, start, end)

        with Database() as db, db.session() as session:

            basins = (
                session.query(NhcFcstTable.basin)
                .distinct()
                .filter(
                    and_(
                        or_(
                            NhcFcstTable.advisory_start >= time_limits["start"],
                            NhcFcstTable.advisory_end >= time_limits["start"],
                        ),
                        or_(
                            NhcFcstTable.advisory_start <= time_limits["end"],
                            NhcFcstTable.advisory_end <= time_limits["end"],
                        ),
                    )
                )
                .all()
            )
            storm_years = (
                session.query(NhcFcstTable.storm_year)
                .distinct()
                .filter(
                    and_(
                        or_(
                            NhcFcstTable.advisory_start >= time_limits["start"],
                            NhcFcstTable.advisory_end >= time_limits["start"],
                        ),
                        or_(
                            NhcFcstTable.advisory_start <= time_limits["end"],
                            NhcFcstTable.advisory_end <= time_limits["end"],
                        ),
                    )
                )
                .all()
            )

            storms = (
                session.query(
                    NhcFcstTable.basin,
                    NhcFcstTable.storm_year,
                    NhcFcstTable.storm,
                )
                .distinct()
                .filter(
                    and_(
                        or_(
                            NhcFcstTable.advisory_start >= time_limits["start"],
                            NhcFcstTable.advisory_end >= time_limits["start"],
                        ),
                        or_(
                            NhcFcstTable.advisory_start <= time_limits["end"],
                            NhcFcstTable.advisory_end <= time_limits["end"],
                        ),
                    )
                )
                .order_by(NhcFcstTable.basin, NhcFcstTable.storm)
                .all()
            )

            storm_data = {}
            for y in storm_years:
                storm_data[y[0]] = {}
                for b in basins:
                    storm_data[y[0]][b[0]] = {}

            for storm in storms:
                b = storm[0]
                y = storm[1]
                n = storm[2]

                this_storm = (
                    session.query(
                        NhcFcstTable.advisory,
                        NhcFcstTable.advisory_start,
                        NhcFcstTable.advisory_end,
                        NhcFcstTable.advisory_duration_hr,
                    )
                    .filter(
                        NhcFcstTable.basin == b,
                        NhcFcstTable.storm_year == y,
                        NhcFcstTable.storm == n,
                    )
                    .order_by(NhcFcstTable.advisory)
                    .all()
                )

                advisory_list = {}
                for adv in this_storm:
                    a = int(adv[0])
                    adv_str = "{:03d}".format(a)
                    start_trk = adv[1]
                    end_trk = adv[2]
                    duration = adv[3]
                    advisory_list[adv_str] = {
                        "advisory_start": Status.d2s(start_trk),
                        "advisory_end": Status.d2s(end_trk),
                        "duration": duration,
                    }

                storm_data[y][b][n] = advisory_list

        return storm_data
