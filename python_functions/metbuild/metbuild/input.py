class Input:
    def __init__(self, json_data, log, queue, messageid):
        import uuid
        self.__json = json_data
        self.__start_date = None
        self.__end_date = None
        self.__operator = None
        self.__version = None
        self.__filename = None
        self.__format = None
        self.__time_step = None
        self.__nowcast = False
        self.__multiple_forecasts = True
        self.__domains = []
        self.__parse()
        self.__uuid = str(uuid.uuid4())
        self.__log = log
        self.__message = messageid
        self.__queue = queue

    def uuid(self):
        return self.__uuid

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
        return pymetbuild.Date(date.year,date.month,date.day,date.hour,date.minute)

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

            if "nowcast" in self.__json.keys():
                self.__nowcast = self.__json["nowcast"]

            if "multiple_forecasts" in self.__json.keys():
                self.__multiple_forecasts = self.__json["multiple_forecasts"]

            ndomain = len(self.__json["domains"])
            if ndomain == 0:
                raise RuntimeError("You must specify one or more wind domains")
            for i in range(ndomain):
                name = self.__json["domains"][i]["name"]
                service = self.__json["domains"][i]["service"]
                self.__domains.append(
                    Domain(name, service, self.__json["domains"][i]))
        except KeyError as e:
            if self.__log:
                self.__log.error("Could not parse the input json data: ",e)
                self.__log.debug("Deleting message "+self.__message+" from the queue")
            else:
                print("[ERROR]: Could not parse the input json dataset: ",e)
            if self.__queue:
                self.__queue.delete_message(self.__message)
            sys.exit(1)

