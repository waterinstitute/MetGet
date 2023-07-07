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
class Isotach:
    def __init__(self, speed, d1=0, d2=0, d3=0, d4=0):
        self.__speed = speed
        self.__distance = [d1, d2, d3, d4]

    def set_speed(self, value):
        self.__speed = value

    def speed(self):
        return self.__speed

    def set_distance(self, quadrant, distance):
        if 0 <= quadrant < 4:
            self.__distance[quadrant] = distance

    def distance(self, quadrant):
        if 0 <= quadrant < 4:
            return self.__distance[quadrant]
        return 0

    def print(self, n=0):
        isoline = "Isotach".rjust(n)
        line = "{:d}: {:.1f} {:.1f} {:.1f} {:.1f}".format(
            self.__speed,
            self.__distance[0],
            self.__distance[1],
            self.__distance[2],
            self.__distance[3],
        )
        print(isoline, line)
