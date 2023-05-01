VALID_SERVICES = ["gfs-ncep", "gefs-ncep", "nam-ncep", "hwrf", "coamps-tc"]


class Domain:
    def __init__(self, name, service, json, no_construct=False):
        from metget_api.metbuild.windgrid import WindGrid

        self.__valid = True
        self.__name = name
        self.__service = service
        self.__basin = None
        self.__advisory = None
        self.__storm_year = None
        self.__tau = None
        self.__no_construct = no_construct
        if self.__service not in VALID_SERVICES:
            self.__valid = False
        self.__json = json
        try:
            self.__grid = WindGrid(self.__json, self.__no_construct)
            if not self.__grid.valid():
                self.__valid = False
        except Exception as e:
            self.__valid = False
            raise
        self.__storm = None
        self.__get_storm()
        self.__get_basin()
        self.__get_advisory()
        self.__get_tau()
        self.__get_storm_year()
        self.__get_ensemble_member()

    def storm(self):
        return self.__storm

    def basin(self):
        return self.__basin

    def advisory(self):
        return self.__advisory

    def ensemble_member(self):
        return self.__ensemble_member

    def tau(self):
        return self.__tau

    def storm_year(self):
        return self.__storm_year

    def name(self):
        return self.__name

    def service(self):
        return self.__service

    def grid(self):
        return self.__grid

    def json(self):
        return self.__json

    def valid(self):
        return self.__valid

    def __get_storm(self):
        if self.service() == "hwrf" or self.service() == "coamps-tc":
            if "storm" in self.__json:
                self.__storm = self.__json["storm"]
            else:
                self.__valid = False
        else:
            self.__storm = None

    def __get_basin(self):
        if self.service() == "nhc":
            if "basin" in self.__json:
                self.__basin = self.__json["basin"]
            else:
                self.__valid = False
        else:
            self.__basin = None

    def __get_advisory(self):
        if self.service() == "nhc":
            if "advisory" in self.__json:
                self.__advisory = self.__json["advisory"]
            else:
                self.__valid = False
        else:
            self.__advisory = None

    def __get_storm_year(self):
        if self.service() == "nhc":
            if "storm_year" in self.__json:
                self.__storm_year = self.__json["storm_year"]
            else:
                self.__storm_year = self.__start_date.year()
        else:
            self.__storm_year = None

    def __get_tau(self):
        if "tau" in self.__json:
            self.__tau = self.__json["tau"]
        else:
            self.__tau = 0

    def __get_ensemble_member(self):
        if self.service() == "gefs-ncep":
            if "ensemble_member" in self.__json:
                self.__ensemble_member = self.__json["ensemble_member"]
            else:
                self.__valid = False
        else:
            self.__ensemble_member = None
