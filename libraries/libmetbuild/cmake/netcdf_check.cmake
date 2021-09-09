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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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
# ##############################################################################
# NETCDF
# ##############################################################################
if(NOT "${NETCDFHOME}" STREQUAL "")
  set(NETCDF_DIR
      "${NETCDFHOME}"
      CACHE STRING "Location of NETCDF Library")
elseif(NOT $ENV{NETCDFHOME} STREQUAL "")
  set(NETCDF_DIR
      $ENV{NETCDFHOME}
      CACHE STRING "Locatin of NETCDF Library")
endif(NOT "${NETCDFHOME}" STREQUAL "")

find_package(NetCDF REQUIRED)

set(NETCDF_AdditionalLibs
    ""
    CACHE STRING "Additional libraries that may be required for netCDF")

if(NOT NETCDF_FOUND)
  message(SEND_ERROR "Specify the netCDF path on the following screen")
else(NOT NETCDF_FOUND)

  set(netcdf_cxx_code
      "
	#include <netcdf.h>
	int main(){
		int ncid,varid;
		int ierr = nc_def_var_deflate(ncid,varid,1,2,2);
		return 0;
	}
")
  file(WRITE "${CMAKE_BINARY_DIR}/CMakeFiles/netcdf_c_check.cpp"
       "${netcdf_cxx_code}")
  try_compile(
    NC_DEFLATE_FOUND "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/netcdf_c_check.cpp"
    CMAKE_FLAGS "-DINCLUDE_DIRECTORIES=${NETCDF_INCLUDE_DIRS}"
    LINK_LIBRARIES "${NETCDF_LIBRARIES}"
    LINK_LIBRARIES "${NETCDF_AdditionalLibs}"
    OUTPUT_VARIABLE LOG1)

  if(NC_DEFLATE_FOUND)
    set(NETCDF_LINKER_FLAG "${NETCDF_LIBRARIES}")
  else(NC_DEFLATE_FOUND)
    message(SEND_ERROR "The netCDF library is not functional.")
  endif(NC_DEFLATE_FOUND)
endif(NOT NETCDF_FOUND)
# ##############################################################################
