VALID_SERVICES = ["gfs-ncep", "nam-ncep", "hwrf"]


class Domain:
    def __init__(self, name, service, json, no_construct=False):
        from metbuild.windgrid import WindGrid
        self.__valid = True
        self.__name = name
        self.__service = service
        if self.__service not in VALID_SERVICES:
            self.__valid = False
        self.__json = json
        try:
            self.__grid = WindGrid(self.__json, no_construct)
            if not self.__grid.valid():
                self.__valid = False
        except:
            self.__valid = False
            raise
        self.__storm = None
        self.__get_storm()

    def storm(self):
        return self.__storm

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
        if self.service() == "hwrf":
            if "storm" in self.__json:
                self.__storm = self.__json["storm"]
            else:
                self.__valid = False
        else:
            self.__storm = None

