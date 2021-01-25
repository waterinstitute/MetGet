class Input:
    def __init__(self, json_data):
        import uuid
        self.__json = json_data
        self.__start_date = None
        self.__end_date = None
        self.__operator = None
        self.__version = None
        self.__filename = None
        self.__format = None
        self.__time_step = None
        self.__domains = []
        self.__parse()
        self.__uuid = str(uuid.uuid4())

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

    def end_date(self):
        return self.__end_date

    def time_step(self):
        return self.__time_step

    def num_domains(self):
        return len(self.__domains)

    def domain(self, index):
        return self.__domains[index]

    def __parse(self):
        import dateutil.parser
        from domain import Domain
        from windgrid import WindGrid
        self.__version = self.__json["version"]
        self.__operator = self.__json["operator"]
        self.__start_date = dateutil.parser.parse(self.__json["start_date"])
        self.__start_date = self.__start_date.replace(tzinfo=None)
        self.__end_date = dateutil.parser.parse(self.__json["end_date"])
        self.__end_date = self.__end_date.replace(tzinfo=None)
        self.__time_step = self.__json["time_step"]
        self.__filename = self.__json["filename"]
        self.__format = self.__json["format"]
        ndomain = len(self.__json["domain"])
        if ndomain == 0:
            raise RuntimeError("You must specify one or more wind domains")
        for i in range(ndomain):
            name = self.__json["domain"][i]["name"]
            service = self.__json["domain"][i]["service"]
            self.__domains.append(
                Domain(name, service, WindGrid(json=self.__json["domain"][i])))
