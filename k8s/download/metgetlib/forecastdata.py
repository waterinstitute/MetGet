#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
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
# Organization: The Water Institute
#
###################################################################################################
class ForecastData:
    def __init__(self, pressure_method):
        from datetime import datetime

        self.__x = 0.0
        self.__y = 0.0
        self.__maxwind = 0.0
        self.__maxgust = 0.0
        self.__pressure = -1
        self.__time = datetime(2000, 1, 1)
        self.__isotach = {}
        self.__forecastHours = 0
        self.__heading = -999
        self.__forward_speed = -999
        self.__pressureMethod = pressure_method

    def set_storm_center(self, x, y):
        self.__x = x
        self.__y = y

    def storm_center(self):
        return self.__x, self.__y

    def set_time(self, time):
        self.__time = time

    def time(self):
        return self.__time

    def set_forecast_hour(self, hour):
        self.__forecastHours = hour

    def forecast_hour(self):
        return self.__forecastHours

    def set_max_wind(self, speed):
        self.__maxwind = speed

    def max_wind(self):
        return self.__maxwind

    def set_max_gust(self, speed):
        self.__maxgust = speed

    def max_gust(self):
        return self.__maxgust

    def set_pressure(self, pressure):
        self.__pressure = pressure

    def set_forward_speed(self, speed):
        self.__forward_speed = speed

    def forward_speed(self):
        return self.__forward_speed

    def set_heading(self, heading):
        self.__heading = heading

    def heading(self):
        return self.__heading

    def compute_pressure(self, vmax_global=0, last_vmax=0, last_pressure=0):
        if self.__pressureMethod == "knaffzehr":
            self.__pressure = self.compute_pressure_knaffzehr(self.__maxwind)
        elif self.__pressureMethod == "dvorak":
            self.__pressure = self.compute_pressure_dvorak(self.__maxwind)
        elif self.__pressureMethod == "ah77":
            self.__pressure = self.compute_pressure_ah77(self.__maxwind)
        elif self.__pressureMethod == "asgs2012":
            self.__pressure = self.compute_pressure_asgs2012(
                self.__maxwind, vmax_global, last_vmax, last_pressure
            )
        elif self.__pressureMethod == "twoslope":
            self.__pressure = self.compute_pressure_twoslope(
                self.__maxwind, last_vmax, last_pressure
            )
        else:
            raise RuntimeError("No valid pressure method found")

    @staticmethod
    def compute_pressure_knaffzehr(wind):
        return ForecastData.compute_pressure_curvefit(wind, 1010.0, 2.3, 0.760)

    @staticmethod
    def compute_pressure_dvorak(wind):
        return ForecastData.compute_pressure_curvefit(wind, 1015.0, 3.92, 0.644)

    @staticmethod
    def compute_pressure_ah77(wind):
        return ForecastData.compute_pressure_curvefit(wind, 1010.0, 3.4, 0.644)

    @staticmethod
    def compute_pressure_curvefit(wind_speed, a, b, c):
        return a - ((wind_speed * 0.514444) / b) ** (1.0 / c)

    @staticmethod
    def compute_pressure_courtneyknaff(wind_speed, forward_speed, eye_latitude):
        background_pressure = 1013.0

        # Below from Courtney and Knaff 2009
        vsrm1 = wind_speed * 1.5 * forward_speed ** 0.63

        rmax = (
            66.785 - 0.09102 * wind_speed + 1.0619 * (eye_latitude - 25.0)
        )  # Knaff and Zehr 2007

        # Two options for v500 ... I assume that vmax is
        # potentially more broadly applicable than r34
        # option 1
        # v500 = r34 / 9.0 - 3.0

        # option 2
        v500 = wind_speed * (
            (66.785 - 0.09102 * wind_speed + 1.0619 * (eye_latitude - 25)) / 500
        ) ** (0.1147 + 0.0055 * wind_speed - 0.001 * (eye_latitude - 25))

        # Knaff and Zehr computes v500c
        v500c = wind_speed * (rmax / 500) ** (
            0.1147 + 0.0055 * wind_speed - 0.001 * (eye_latitude - 25.0)
        )

        # Storm size parameter
        S = max(v500 / v500c, 0.4)

        if eye_latitude < 18.0:
            dp = 5.962 - 0.267 * vsrm1 - (vsrm1 / 18.26) ** 2.0 - 6.8 * S
        else:
            dp = (
                23.286
                - 0.483 * vsrm1
                - (vsrm1 / 24.254) ** 2.0
                - 12.587 * S
                - 0.483 * eye_latitude
            )

        return dp + background_pressure

    @staticmethod
    def compute_initial_pressure_estimate_asgs(wind, last_vmax, last_pressure):

        if last_pressure == 0:
            if last_vmax == 0:
                raise RuntimeError("No valid prior wind speed given")
            # Estimate the last pressure if none is given
            last_pressure = ForecastData.compute_pressure_dvorak(last_vmax)

        # pressure variable
        p = last_pressure

        if wind > last_vmax:
            p = 1040.0 - 0.877 * wind
            if p > last_pressure:
                p = last_pressure - 0.877 * (wind - last_vmax)
        elif wind < last_vmax:
            p = 1000.0 - 0.65 * wind
            if p < last_pressure:
                p = last_pressure + 0.65 * (last_vmax - wind)

        return p

    @staticmethod
    def compute_pressure_asgs2012(wind, vmax_global, last_vmax, last_pressure):
        p = ForecastData.compute_initial_pressure_estimate_asgs(
            wind, last_vmax, last_pressure
        )
        if wind <= 35:
            if vmax_global > 39:
                p = ForecastData.compute_pressure_dvorak(wind)
            else:
                p = ForecastData.compute_pressure_ah77(wind)

        return p

    @staticmethod
    def compute_pressure_twoslope(wind, last_vmax, last_pressure):
        p = ForecastData.compute_initial_pressure_estimate_asgs(
            wind, last_vmax, last_pressure
        )
        if wind < 30:
            p = last_pressure

        return p

    def pressure(self):
        return self.__pressure

    def set_isotach(self, speed, d1, d2, d3, d4):
        from .isotach import Isotach

        self.__isotach[speed] = Isotach(speed, d1, d2, d3, d4)

    def isotach(self, speed):
        return self.__isotach[speed]

    def nisotachs(self):
        return len(self.__isotach)

    def isotach_levels(self):
        levels = []
        for key in self.__isotach:
            levels.append(key)
        return levels

    def print(self):
        print("Forecast Data for: " + self.__time.strftime("%Y-%m-%d %HZ"))
        print("          Storm Center: ", "{:.2f}, {:.2f}".format(self.__x, self.__y))
        print("              Max Wind: ", "{:.1f}".format(self.__maxwind))
        print("              Max Gust: ", "{:.1f}".format(self.__maxgust))
        print("              Pressure: ", "{:.1f}".format(self.__pressure))
        print("         Forecast Hour: ", "{:.1f}".format(self.__forecastHours))
        if not self.__forward_speed == -999:
            print("         Forward Speed: ", "{:.1f}".format(self.__forward_speed))
        if not self.__heading == -999:
            print("               Heading: ", "{:.1f}".format(self.__heading))
        print("    Number of Isotachs: ", self.nisotachs())
        print("        Isotach Levels: ", self.isotach_levels())
        for level in self.isotach_levels():
            self.isotach(level).print(24)
