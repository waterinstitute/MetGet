class WindGrid:
    def __init__(self, json=None):
        import pymetbuild
        self.__json = json
        self.__wg = None
        self.__construct()

    def grid_object(self):
        return self.__wg

    def bottom_left(self):
        return self.__wg.bottom_left()

    def bottom_right(self):
        return self.__wg.bottom_right()

    def top_left(self):
        return self.__wg.top_left()

    def top_right(self):
        return self.__wg.top_right()

    def di(self):
        return self.__wg.di()

    def dj(self):
        return self.__wg.dj()

    def rotation(self):
        return self.__wg.rotation()

    def nx(self):
        return self.__wg.nx()

    def ny(self):
        return self.__wg.ny()

    @staticmethod
    def predefined_domain(predefined_domain_name):
        predefined_domain_name = predefined_domain_name.lower()
        if predefined_domain_name == "wnat":
            return -98, 10, -60, 45, 0.25, 0.25
        elif predefined_domain_name == "gom":
            return -98, 10, -75, 30, 0.25, 0.25
        elif predefined_domain_name == "global":
            return -180.0, -90.0, 180.0, 90.0, 0.25, 0.25
        raise RuntimeError("No matching predefined domain found")

    def __construct(self):
        import pymetbuild
        xinit = None
        yinit = None
        xend = None
        yend = None
        rotation = None
        dx = None
        dy = None
        nx = None
        ny = None
        if self.__json:
            if "x_init" in self.__json.keys():
                xinit = self.__json["x_init"]
            if "y_init" in self.__json.keys():
                yinit = self.__json["y_init"]
            if "x_end" in self.__json.keys():
                xend = self.__json["x_end"]
            if "y_end" in self.__json.keys():
                yend = self.__json["y_end"]
            if "rotation" in self.__json.keys():
                rotation = self.__json["rotation"]
            if "di" in self.__json.keys():
                dx = self.__json["di"]
            if "dj" in self.__json.keys():
                dy = self.__json["dj"]
            if "ni" in self.__json.keys():
                nx = self.__json["ni"]
            if "nj" in self.__json.keys():
                ny = self.__json["nj"]
            if "predefined_domain" in self.__json.keys():
                xinit, yinit, xend, yend, dx, dy = self.predefined_domain(
                    self.__json["predefined_domain"])

        if xinit is None or yinit is None:
            raise RuntimeError("Lower left corner not specified")
        if (xend is None or yend is None) and (nx is None or ny is None):
            raise RuntimeError("Must specify xur/yur or nx/ny")
        if (xend is not None or yend is not None) and (nx is not None or ny is not None):
            raise RuntimeError("Cannot specify both xur/yur and nx/ny")
        if (xend is not None and yend is None) or (yend is not None and xend is None):
            raise RuntimeError("Must specify both of xur/yur")
        if (nx is not None and ny is not None) or (ny is not None and nx is None):
            raise RuntimeError("Must specify both of nx/ny")
        if rotation is not None and (xend is not None or yend is not None):
            raise RuntimeError("Cannot specify rotation with xur/yur")
        if rotation is not None and not (nx is not None and ny is not None):
            raise RuntimeError("Must specify nx/ny with rotation")
        if dx is None or dy is None:
            raise RuntimeError("Must specify dx/dy")

        if xinit is not None and yinit is not None and xend is not None and yend is not None:
            self.__wg = pymetbuild.WindGrid(xinit,yinit,xend,yend,dx,dy)
        elif xinit is not None and yinit is not None  and nx is not None and ny is not None:
            if rotation is not None:
                rotation = 0.0
            self.__wg = pymetbuild.WindGrid(xinit,yinit,nx,ny,dx,dy,rotation)

