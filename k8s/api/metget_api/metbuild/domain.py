VALID_SERVICES = ["gfs-ncep", "gefs-ncep", "nam-ncep", "hwrf", "coamps-tc"]


class Domain:
    def __init__(self, name, service, json):
        from metget_api.metbuild.windgrid import WindGrid

        self.__valid = True
        self.__name = name
        self.__service = service
        if self.__service not in VALID_SERVICES:
            self.__valid = False
        self.__json = json
        try:
            self.__grid = WindGrid(self.__json)
            if not self.__grid.valid():
                self.__valid = False
        except:
            self.__valid = False
            raise
        self.__storm = None
        self.__get_storm()
        self.__get_ensemble_member()

    def storm(self):
        return self.__storm

    def ensemble_member(self):
        return self.__ensemble_member

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

    def __get_ensemble_member(self):
        if self.service() == "gefs-ncep":
            if "ensemble_member" in self.__json:
                self.__ensemble_member = self.__json["ensemble_member"]
            else:
                self.__valid = False
        else:
            self.__ensemble_member = None
