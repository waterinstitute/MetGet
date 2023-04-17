#!/usr/bin/env python3


class MetGetStatus:
    def __init__(self):
        pass

    def get_status(self, status_type: str):
        """
        This method is used to generate the status from the various sources
        """

        if status_type == "gfs":
            return self.__get_status_gfs()
        elif status_type == "nam":
            return self.__get_status_nam()
        elif status_type == "hwrf":
            return self.__get_status_hwrf()
        elif status_type == "hrrr":
            return self.__get_status_hrrr()
        elif status_type == "hrrr-alaksa":
            return self.__get_status_hrrr_alaska()
        elif status_type == "nhc":
            return self.__get_status_nhc()
        elif status_type == "coamps":
            return self.__get_status_coamps()

    def __get_status_generic(self, table_type: any) -> dict:
        from database import Database

        db = Database()
        session = db.session()

        unique_cycles = (
            session.query(table_type.forecastcycle)
            .distinct()
            .all()
            .order_by(table_type.forecastcycle.desc())
        )

        for cycle in unique_cycles:
            print(cycle)

        return {}

    def __get_status_gfs(self) -> dict:
        from tables import GfsTable

        return self.__get_status_generic(GfsTable)

    def __get_status_nam(self) -> dict:
        from tables import NamTable

        return self.__get_status_generic(NamTable)

    def __get_status_hrrr(self):
        from tables import HrrrTable

        return self.__get_status_generic(HrrrTable)

    def __get_status_hrrr_alaska(self):
        from tables import HrrrAlaskaTable

        return self.__get_status_generic(HrrrAlaskaTable)

    def __get_status_hwrf(self):
        pass

    def __get_status_coamps(self):
        pass

    def __get_status_nhc(self):
        pass
