VALID_SERVICES = ["gfs-ncep", "gefs-ncep", "nam-ncep", "hwrf", "coamps-tc"]


class Domain:
    """
    A Domain object is a container for a single domain
    """

    def __init__(self, name: str, service: str, json: dict, no_construct: bool = False):
        """
        Constructor for a Domain object

        Args:
            name (str): The name of the domain
            service (str): The service that provides the data for this domain
            json (dict): The json string that defines the domain
            no_construct (bool): If True, do not construct the grid.  This is useful for testing.
        """
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
        self.__tau = 0
        self.__basin = None
        self.__get_tau()
        self.__get_storm()
        self.__get_ensemble_member()
        self.__get_advisory()

    def storm(self) -> str:
        """
        Returns the storm name for this domain.  If the domain is not a tropical cyclone domain, this will return None.
        """
        return self.__storm

    def ensemble_member(self) -> str:
        """
        Returns the ensemble member for this domain.  If the domain is not an ensemble member, this will return None.
        """
        return self.__ensemble_member

    def basin(self) -> str:
        """
        Returns the basin for this domain.  If the domain is not a tropical cyclone domain, this will return None.
        """
        return self.__basin

    def tau(self) -> int:
        """
        Returns the tau for this domain.
        """
        return self.__tau

    def advisory(self) -> str:
        """
        Returns the advisory for this domain.  If the domain is not a tropical cyclone domain, this will return None.
        """
        return self.__advisory

    def name(self) -> str:
        """
        Returns the name of this domain.
        """
        return self.__name

    def service(self) -> str:
        """
        Returns the service that provides the data for this domain.
        """
        return self.__service

    def grid(self):
        """
        Returns the grid for this domain.
        """
        return self.__grid

    def json(self) -> dict:
        """
        Returns the json string that defines this domain.
        """
        return self.__json

    def valid(self) -> bool:
        """
        Returns True if this domain is valid, False otherwise.
        """
        return self.__valid

    def __get_tau(self):
        """
        Get the tau for this domain.
        """
        if "tau" in self.__json:
            self.__tau = int(self.__json["tau"])
        else:
            self.__tau = 0

    def __get_storm(self):
        """
        Get the storm name for this domain.
        """
        if (
            self.service() == "hwrf"
            or self.service() == "coamps-tc"
            or self.service() == "nhc"
        ):
            if "storm" in self.__json:
                self.__storm = str(self.__json["storm"])
            else:
                self.__valid = False
        else:
            self.__storm = None

    def __get_ensemble_member(self):
        """
        Get the ensemble member for this domain.
        """
        if self.service() == "gefs-ncep":
            if "ensemble_member" in self.__json:
                self.__ensemble_member = self.__json["ensemble_member"]
            else:
                self.__valid = False
        else:
            self.__ensemble_member = None

    def __get_advisory(self):
        """
        Get the advisory for this domain.
        """
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