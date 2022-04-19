# ##############################################################################
# MetBuild Cmake Build System
#
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
# Author: Zach Cobell Contact: zcobell@thewaterinstitute.org
#
# ##############################################################################
set(ENABLE_FORTRAN
    OFF
    CACHE BOOL "Enable Fortran functionality in eccodes")
set(ENABLE_PYTHON
    OFF
    CACHE BOOL "Enable Python functionality in eccodes")
set(ENABLE_NETCDF
    OFF
    CACHE BOOL "Enable NetCDF functionality in eccodes")
set(ENABLE_PRODUCT_BUFR
    OFF
    CACHE BOOL "Enable BUFR")
set(BUILD_SHARED_LIBS
    OFF
    CACHE BOOL "Enable building shared libraries")
#set(ENABLE_JPG_LIBJASPER
#    OFF
#    CACHE BOOL "Enable JPEG LIBJASPER")

mark_as_advanced(
  ENABLE_WARNINGS
  ENABLE_TESTS
  ENABLE_RPATHS
  ENABLE_RELATIVE_RPATHS
  ENABLE_PYTHON
  ENABLE_PROFILING
  ENABLE_PRODUCT_GRIB
  ENABLE_PRODUCT_BUFR
  ENABLE_PNG
  ENABLE_JPG
  MEMORYCHECK_COMMAND_OPTIONS
  ENABLE_NETCDF
  ENABLE_MEMFS
  ENABLE_JPG_LIBOPENJPEG
  ENABLE_JPG_LIBJASPER
  ENABLE_INSTALL_ECCODES_DEFINIT
  ENABLE_INSTALL_ECCODES_SAMPLES
  ENABLE_FORTRAN
  ENABLE_EXAMPLES
  ENABLE_AEC
  ECMWF_USER
  ECMWF_GIT
  ECBUILD_2_COMPAT_DEPRECATE
  ECBUILD_2_COMPAT
  CMATH_LIBRARIES
  BUILD_SHARED_LIBS)

add_subdirectory(
  ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/eccodes-2.25.0
  ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/eccodes EXCLUDE_FROM_ALL)
# ##############################################################################
