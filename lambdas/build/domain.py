class Domain:
    def __init__(self, name, service, grid):
        self.__name = name
        self.__service = service
        self.__grid = grid
        self.__met_data = None

    def set_met_data(self, met_data):
        self.__met_data = met_data

    def met_data(self):
        return self.__met_data

    def name(self):
        return self.__name

    def service(self):
        return self.__service

    def grid(self):
        return self.__grid
