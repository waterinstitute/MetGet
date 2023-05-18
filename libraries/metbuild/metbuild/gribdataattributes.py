class GribDataAttributes:
    def __init__(
        self,
        name: str,
        table: str,
        bucket: str,
        variables: dict,
        cycles: list,
        ensemble_members: list = None,
    ):
        self.__name = name
        self.__table = table
        self.__bucket = bucket
        self.__cycles = cycles
        self.__ensemble_members = ensemble_members

        self.__variables = []
        for variable in variables.keys():
            self.__variables.append(
                {
                    "name": variable,
                    "long_name": variables[variable],
                }
            )

    def name(self) -> str:
        return self.__name

    def table(self) -> str:
        return self.__table

    def bucket(self) -> str:
        return self.__bucket

    def variables(self) -> dict:
        return self.__variables

    def cycles(self) -> list:
        return self.__cycles

    def ensemble_members(self) -> list:
        return self.__ensemble_members


NCEP_GFS = GribDataAttributes(
    "GFS-NCEP",
    "gfs_ncep",
    "noaa-gfs-bdp-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "ice": "ICEC:surface",
        "precip_rate": "PRATE",
        "humidity": "RH:30-0 mb above ground",
        "temperature": "TMP:30-0 mb above ground",
    },
    [0, 6, 12, 18],
)

NCEP_NAM = GribDataAttributes(
    "NAM-NCEP",
    "nam_ncep",
    "noaa-nam-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "accumulated_precip": "APCP",
        "humidity": "RH:30-0 mb above ground",
        "temperature": "TMP:30-0 mb above ground",
    },
    [0, 6, 12, 18],
)

NCEP_GEFS = GribDataAttributes(
    "GEFS-NCEP",
    "gefs_ncep",
    "noaa-gefs-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "ice": "ICETK:surface",
        "accumulated_precip": "APCP",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [0, 6, 12, 18],
    # ...GEFS ensemble members:
    #   Valid perturbations for gefs are:
    #   avg => ensemble mean
    #   c00 => control
    #   pXX => perturbation XX (1-30)
    ["avg", "c00", *[f"p{i:02d}" for i in range(1, 31)]],
)

NCEP_HRRR = GribDataAttributes(
    "HRRR-NCEP",
    "hrrr_ncep",
    "noaa-hrrr-bdp-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "MSLMA:mean sea level",
        "ice": "ICEC:surface",
        "precip_rate": "PRATE",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [i for i in range(0, 24)],
)

NCEP_HRRR_ALASKA = GribDataAttributes(
    "HRRR-ALASKA-NCEP",
    "hrrr_alaska_ncep",
    "noaa-hrrr-bdp-pds",
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "MSLMA:mean sea level",
        "ice": "ICEC:surface",
        "precip_rate": "PRATE",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [i for i in range(0, 24)],
)

NCEP_HWRF = GribDataAttributes(
    "HWRF",
    "hwrf",
    None,
    {
        "uvel": "UGRD:10 m above ground",
        "vvel": "VGRD:10 m above ground",
        "press": "PRMSL",
        "accumulated_precip": "APCP",
        "humidity": "RH:2 m above ground",
        "temperature": "TMP:2 m above ground",
    },
    [0, 6, 12, 18],
)
