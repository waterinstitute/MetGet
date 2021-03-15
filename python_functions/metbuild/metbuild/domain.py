class Domain:
    def __init__(self, name, service, json):
        from metbuild.windgrid import WindGrid
        self.__name = name
        self.__service = service
        self.__json = json
        self.__grid = WindGrid(self.__json)

    def name(self):
        return self.__name

    def service(self):
        return self.__service

    def grid(self):
        return self.__grid

    def json(self):
        return self.__json
