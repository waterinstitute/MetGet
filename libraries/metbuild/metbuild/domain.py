import logging
from .windgrid import WindGrid

VALID_SERVICES = [
    "gfs-ncep",
    "gefs-ncep",
    "nam-ncep",
    "wpc-ncep",
    "hwrf",
    "coamps-tc",
    "coamps-ctcx",
    "nhc",
    "hrrr-conus",
    "hrrr-alaska",
]


class Domain:
    """
    Domain class. This class is used to store the domain information for a
    request
    """

    def __init__(self, name, service, json, no_construct=False):
        """
        Constructor for the Domain class

        Args:
            name: The name of the domain
            service: The service used to generate the domain
            json: The json object containing the domain information
            no_construct: If True, do not construct the WindGrid object
        """

        log = logging.getLogger(__name__)

        self.__valid = True
        self.__name = name
        self.__service = service
        self.__basin = None
        self.__advisory = None
        self.__storm_year = None
        self.__tau = None
        self.__no_construct = no_construct
        if self.__service not in VALID_SERVICES:
            log.warning(
                "Domain invalid because {:s} is not a valid service".format(
                    self.__service
                )
            )
            self.__valid = False
        self.__json = json
        try:
            self.__grid = WindGrid(self.__json, self.__no_construct)
            if not self.__grid.valid():
                log.warning(
                    "Domain invalid because a valid WindGrid object could not be constructed"
                )
                self.__valid = False
        except Exception as e:
            log.warning(
                "Domain invalid because exception was thrown: {:s}".format(str(e))
            )
            self.__valid = False
            raise
        self.__storm = None
        self.__get_storm()
        self.__get_basin()
        self.__get_advisory()
        self.__get_tau()
        self.__get_storm_year()
        self.__get_ensemble_member()

    def storm(self) -> str:
        """
        Returns the storm name for the domain.
        If the domain does not have a storm, this will return None

        Returns:
            The storm name for the domain
        """
        return self.__storm

    def basin(self) -> str:
        """
        Returns the basin name for the domain.
        If the domain does not have a storm, this will return None

        Returns:
            The basin name for the domain
        """
        return self.__basin

    def advisory(self) -> str:
        """
        Returns the advisory name for the domain.
        If the domain does not have a storm, this will return None

        Returns:
            The advisory name for the domain
        """
        return self.__advisory

    def ensemble_member(self) -> str:
        """
        Returns the ensemble member for the domain.
        If the domain does not have an ensemble member, this will return None

        Returns:
            The ensemble member for the domain
        """
        return self.__ensemble_member

    def tau(self) -> int:
        """
        Returns the tau (skipping time) for the domain.
        If the domain does not have a tau, it will return 0

        Returns:
            The tau for the domain
        """
        return self.__tau

    def storm_year(self) -> int:
        """
        Returns the storm year for the domain.
        If the domain does not have a storm, it will return None

        Returns:
            The storm year for the domain
        """
        return self.__storm_year

    def name(self) -> str:
        """
        Returns the name of the domain

        Returns:
            The name of the domain
        """
        return self.__name

    def service(self) -> str:
        """
        Returns the service used to generate the domain

        Returns:
            The service used to generate the domain
        """
        return self.__service

    def grid(self) -> WindGrid:
        """
        Returns the grid for the domain

        Returns:
            The grid for the domain
        """
        return self.__grid

    def json(self) -> dict:
        """
        Returns the json object for the domain

        Returns:
            The json object for the domain
        """
        return self.__json

    def valid(self) -> bool:
        """
        Returns whether the domain is valid

        Returns:
            True if the domain is valid, False otherwise
        """
        return self.__valid

    def __get_storm(self) -> None:
        """
        Gets the storm name for the domain from the json object if the service is hwrf or coamps-tc

        Returns:
            None
        """
        if (
            self.service() == "hwrf"
            or self.service() == "coamps-tc"
            or self.service() == "coamps-ctcx"
            or self.service() == "nhc"
        ):
            if "storm" in self.__json:
                self.__storm = str(self.__json["storm"])
            else:
                self.__valid = False
        else:
            self.__storm = None

    def __get_basin(self) -> None:
        """
        Gets the basin name for the domain from the json object if the service is nhc

        Returns:
            None
        """
        if self.service() == "nhc":
            if "basin" in self.__json:
                self.__basin = self.__json["basin"]
            else:
                self.__valid = False
        else:
            self.__basin = None

    def __get_advisory(self) -> None:
        """
        Gets the advisory name for the domain from the json object if the service is nhc

        Returns:
            None
        """
        if self.service() == "nhc":
            if "advisory" in self.__json:
                self.__advisory = str(self.__json["advisory"])
            else:
                self.__valid = False
        else:
            self.__advisory = None

    def __get_storm_year(self) -> None:
        """
        Gets the storm year for the domain from the json object if the service is nhc

        Returns:
            None
        """
        from datetime import datetime

        if self.service() == "nhc":
            if "storm_year" in self.__json:
                self.__storm_year = self.__json["storm_year"]
            else:
                self.__storm_year = datetime.now().year
        else:
            self.__storm_year = None

    def __get_tau(self) -> None:
        """
        Gets the tau for the domain from the json object if the service is nhc

        Returns:
            None
        """
        if "tau" in self.__json:
            self.__tau = self.__json["tau"]
        else:
            self.__tau = 0

    def __get_ensemble_member(self) -> None:
        """
        Gets the ensemble member for the domain from the json object if the service is gefs-ncep

        Returns:
            None
        """
        if self.service() == "gefs-ncep" or self.service() == "coamps-ctcx":
            if "ensemble_member" in self.__json:
                self.__ensemble_member = self.__json["ensemble_member"]
            else:
                self.__valid = False
        else:
            self.__ensemble_member = None
