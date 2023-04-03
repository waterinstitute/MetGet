VALID_DATA_TYPES = ["wind_pressure", "rain", "ice", "humidity", "temperature"]


class Input:
    def __init__(self, json_data):
        import uuid

        self.__json = json_data
        self.__data_type = "wind_pressure"
        self.__start_date = None
        self.__end_date = None
        self.__operator = None
        self.__version = None
        self.__filename = None
        self.__format = None
        self.__time_step = None
        self.__nowcast = False
        self.__backfill = False
        self.__compression = False
        self.__epsg = 4326
        self.__multiple_forecasts = True
        self.__domains = []
        self.__parse()
        self.__uuid = str(uuid.uuid4())

    def uuid(self):
        return self.__uuid

    def data_type(self):
        return self.__data_type

    def format(self):
        return self.__format

    def filename(self):
        return self.__filename

    def json(self):
        return self.__json

    def version(self):
        return self.__version

    def operator(self):
        return self.__operator

    def start_date(self):
        return self.__start_date

    @staticmethod
    def date_to_pmb(date):
        from datetime import datetime
        import pymetbuild

        return pymetbuild.Date(date.year, date.month, date.day, date.hour, date.minute)

    def start_date_pmb(self):
        return Input.date_to_pmb(self.__start_date)

    def end_date(self):
        return self.__end_date

    def end_date_pmb(self):
        return Input.date_to_pmb(self.__end_date)

    def time_step(self):
        return self.__time_step

    def num_domains(self):
        return len(self.__domains)

    def domain(self, index):
        return self.__domains[index]

    def nowcast(self):
        return self.__nowcast

    def multiple_forecasts(self):
        return self.__multiple_forecasts

    def backfill(self):
        return self.__backfill

    def compression(self):
        return self.__compression

    def epsg(self):
        return self.__epsg

    def __parse(self):
        import sys
        import logging
        import dateutil.parser
        from metbuild.domain import Domain

        log = logging.getLogger(__name__)

        try:
            self.__version = self.__json["version"]
            self.__operator = self.__json["creator"]
            self.__start_date = dateutil.parser.parse(self.__json["start_date"])
            self.__start_date = self.__start_date.replace(tzinfo=None)
            self.__end_date = dateutil.parser.parse(self.__json["end_date"])
            self.__end_date = self.__end_date.replace(tzinfo=None)
            self.__time_step = self.__json["time_step"]
            self.__filename = self.__json["filename"]
            self.__format = self.__json["format"]

            if self.__format == "owi-netcdf" or self.__format == "hec-netcdf":
                if not self.__filename[-3:-1] == "nc":
                    self.__filename = self.__filename + ".nc"

            if "data_type" in self.__json.keys():
                self.__data_type = self.__json["data_type"]
                if self.__data_type not in VALID_DATA_TYPES:
                    raise RuntimeError("Invalid data type specified")

            if "backfill" in self.__json.keys():
                self.__backfill = self.__json["backfill"]

            if "epsg" in self.__json.keys():
                self.__epsg = self.__json["epsg"]

            if "nowcast" in self.__json.keys():
                self.__nowcast = self.__json["nowcast"]

            if "multiple_forecasts" in self.__json.keys():
                self.__multiple_forecasts = self.__json["multiple_forecasts"]

            if "compression" in self.__json.keys():
                self.__compression = self.__json["compression"]

            ndomain = len(self.__json["domains"])
            if ndomain == 0:
                raise RuntimeError("You must specify one or more wind domains")
            for i in range(ndomain):
                name = self.__json["domains"][i]["name"]
                service = self.__json["domains"][i]["service"]
                self.__domains.append(Domain(name, service, self.__json["domains"][i]))
        except KeyError as e:
            log.error("Could not parse the input json dataset: ", e)
            sys.exit(1)
