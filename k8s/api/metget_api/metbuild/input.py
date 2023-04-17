class Input:
    def __init__(self, json_data):
        self.__json = json_data
        self.__start_date = None
        self.__end_date = None
        self.__operator = None
        self.__version = None
        self.__filename = None
        self.__format = None
        self.__time_step = None
        self.__nowcast = False
        self.__backfill = False
        self.__strict = False
        self.__multiple_forecasts = True
        self.__valid = True
        self.__dry_run = False
        self.__error = []
        self.__domains = []
        self.__parse()

    def valid(self):
        return self.__valid

    def dry_run(self):
        return self.__dry_run

    def error(self):
        return self.__error

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

    def end_date(self):
        return self.__end_date

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

    def strict(self):
        return self.__strict

    def __parse(self):
        import sys
        import dateutil.parser
        from metbuild.domain import Domain

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

            if "dry_run" in self.__json.keys():
                self.__dry_run = self.__json["dry_run"]

            if "backfill" in self.__json.keys():
                self.__backfill = self.__json["backfill"]

            if "nowcast" in self.__json.keys():
                self.__nowcast = self.__json["nowcast"]

            if "multiple_forecasts" in self.__json.keys():
                self.__multiple_forecasts = self.__json["multiple_forecasts"]

            if "strict" in self.__json.keys():
                self.__strict = self.__json["strict"]

            # ... Sanity check
            if self.__start_date >= self.__end_date:
                self.__error.append("Request dates are not valid")
                self.__valid = False

            ndomain = len(self.__json["domains"])
            if ndomain == 0:
                raise RuntimeError("You must specify one or more wind domains")
            for i in range(ndomain):
                name = self.__json["domains"][i]["name"]
                service = self.__json["domains"][i]["service"]
                d = Domain(
                    name, service, self.__json["domains"][i], True,
                )
                if d.valid():
                    self.__domains.append(d)
                else:
                    if self.__log:
                        self.__log.error("Could not parse domain " + str(i))
                    self.__valid = False
                    self.__error.append("Could not generate domain " + str(i))

        except Exception as e:
            if self.__log:
                self.__log.error("Could not parse the input json data: " + str(e))
            else:
                import traceback

                print(traceback.format_exc())
                print("[ERROR]: Could not parse the input json dataset: " + str(e))
            self.__valid = False
            self.__error.append("Could not parse the input json dataset: " + str(e))
