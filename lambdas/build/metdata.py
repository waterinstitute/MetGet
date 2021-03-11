#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 ADCIRC Development Group
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
#
class Metdata:
    def __init__(self, data_type, files, times):
        from uvpgrib import UvpGrib
        self.__data_type = data_type
        self.__file_list = files
        self.__times = times
        self.__uvp0 = UvpGrib()
        self.__uvp1 = UvpGrib()
        self.__uvpdata0 = None
        self.__uvpdata1 = None

        if not len(files) == len(times):
            raise RuntimeError("File list must have same length as time list")

        if self.__data_type == "gfs" or self.__data_type == "nam" or self.__data_type == "hwrf":
            self.__format = "grb"
        else:
            raise RuntimeError("Invalid data format specified: " +
                               self.__data_type)

    def data_type(self):
        return self.__data_type

    def files(self):
        return self.__file_list

    def times(self):
        return self.__times

    def file(self, index):
        return self.__file_list[index]

    def time(self, index):
        return self.__times[index]

    def format(self):
        return self.__format

    def interpolate_to_grid(self, query_time, wind_grid):
        from uvpgrib import UvpGrib
        import numpy as np
        idx, key0 = min(enumerate(self.__times),
                        key=lambda x: abs(x[1] - query_time))
        if key0 > query_time:
            idx -= 1
        if query_time >= self.__times[-1]:
            file0 = self.__file_list[idx]
            file1 = self.__file_list[idx]
            time0 = self.__times[idx]
            time1 = self.__times[idx]
            weight0 = 1.0
            weight1 = 0.0
        else:
            file0 = self.__file_list[idx]
            file1 = self.__file_list[idx + 1]
            time0 = self.__times[idx]
            time1 = self.__times[idx + 1]
            weight0 = 1.0
            weight1 = 0.0
            weight0 = (time1 - query_time) / (time1 - time0)
            weight1 = 1.0 - weight0

        print("[INFO]: Interpolating at time: ", query_time)
        if self.__uvp1.filename() == file0:
            self.__uvp0 = self.__uvp1
            self.__uvpdata0 = self.__uvpdata1
        elif not self.__uvp0.filename() == file0:
            self.__uvp0 = UvpGrib(file0)
            self.__uvpdata0 = Metdata.__generate_data_arrays(
                self.__uvp0, wind_grid)

        if not self.__uvp1.filename() == file1:
            self.__uvp1 = UvpGrib(file1)
            self.__uvpdata1 = Metdata.__generate_data_arrays(
                self.__uvp1, wind_grid)

        return self.__uvpdata0 * weight0 + self.__uvpdata1 * weight1

    @staticmethod
    def __generate_data_arrays(data, wind_grid):
        import numpy as np
        points = []
        uvp = np.zeros((3, wind_grid.nx(), wind_grid.ny()), dtype=float)
        for i in range(wind_grid.nx()):
            for j in range(wind_grid.ny()):
                x, y = wind_grid.corner(i, j)
                points.append([x, y])
        u, v, p = data.interpolate(points)
        uvp[0] = np.array(u).reshape(wind_grid.nx(), wind_grid.ny())
        uvp[1] = np.array(v).reshape(wind_grid.nx(), wind_grid.ny())
        uvp[2] = np.array(p).reshape(wind_grid.nx(), wind_grid.ny())
        return uvp
