VALID_SERVICES = ["gfs-ncep", "gefs-ncep", "nam-ncep", "hwrf", "coamps-tc"]


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
        self.__ensemble_member = None
        self.__advisory = None
        self.__basin = None
        self.__get_storm()
        self.__get_ensemble_member()
        self.__get_advisory()

    def storm(self) -> str:
        return self.__storm

    def ensemble_member(self) -> str:
        return self.__ensemble_member

    def basin(self) -> str:
        return self.__basin

    def advisory(self) -> str:
        return self.__advisory

    def name(self) -> str:
        return self.__name

    def service(self) -> str:
        return self.__service

    def grid(self):
        return self.__grid

    def json(self) -> str:
        return self.__json

    def valid(self) -> bool:
        return self.__valid

    def __get_storm(self):
        if self.service() == "hwrf" or self.service() == "coamps-tc" or self.service() == "nhc":
            if "storm" in self.__json:
                self.__storm = str(self.__json["storm"])
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

    def __get_advisory(self):
        if self.service() == "nhc":
            if "advisory" in self.__json:
                adv = self.__json["advisory"]
                if type(adv) is int:
                    self.__advisory = "{:03d}".format(adv)
                else:
                    try: 
                        adv_int = int(adv)
                        self.__advisory = "{:03d}".format(adv_int)
                    except:
                        self.__advisory = adv
            else:
                self.__valid = False

            if "basin" in self.__json:
                self.__basin = self.__json["basin"]
            else:
                self.__valid = False
        else:
            self.__advisory = None
            self.__basin = None
