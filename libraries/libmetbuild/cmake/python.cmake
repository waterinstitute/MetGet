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
# SWIG/PYTHON/PERL Note: This will attempt to default to Python3 Give the flag
# -DPYTHON2=ON to force Python2 usage
# ##############################################################################
if(${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION} GREATER_EQUAL 3.12 AND APPLE)
  set(Python3_USE_STATIC_LIBS TRUE)
  set(Python3_FIND_STRATEGY LOCATION)
  find_package(Python3 COMPONENTS Interpreter Development)
else()
  set(Python_USE_STATIC_LIBS TRUE)
  set(Python_FIND_STRATEGY LOCATION)
  find_package(PythonInterp 3)
  find_package(PythonLibs 3)
  if(PythonInterp_FOUND AND PythonLibs_FOUND)
    set(Python3_FOUND TRUE)
    set(Python_USE_MODULE FALSE)
    set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
    set(Python3_INCLUDE_DIRS ${PYTHON_INCLUDE_DIRS})
  endif()
endif()

find_package(SWIG 3.0)
if(SWIG_FOUND AND Python3_FOUND)
  include(${SWIG_USE_FILE})
  if(Python3_FOUND)
    option(PYTHON_TESTING "Test the Python Libraries with CTest" OFF)
    execute_process(
      COMMAND ${Python3_EXECUTABLE} -m site --user-site
      OUTPUT_VARIABLE temp_PYTHON_SITE_DIRECTORY
      OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(PYTHON_INSTALL_DIRECTORY
        ${temp_PYTHON_SITE_DIRECTORY}
        CACHE STRING "Location where Python libraries will be installed")
    mark_as_advanced(CLEAR PYTHON_EXECUTABLE)
  else(Python3_FOUND)
    set(PYTHON_INSTALL_DIRECTORY
        "PYTHON_INSTALL_DIRECTORY-NOTFOUND"
        CACHE STRING "Location where Python libraries will be installed")
  endif(Python3_FOUND)
else()
  message(
    WARNING
      "SWIG/Python libraries could not be found. Python disabled."
  )
endif()
# ##############################################################################
