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
# libmetbuild
# ##############################################################################

set(METBUILD_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Date.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Grib.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Kdtree.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/KdtreePrivate.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Meteorology.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Grid.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Logging.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/OwiNcFile.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/OwiAscii.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/OwiNetcdf.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/OwiAsciiDomain.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/OwiNetcdfDomain.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/RasNetcdf.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/RasNetcdfDomain.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/DelftOutput.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/output/DelftDomain.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Utilities.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Projection.cpp)

add_library(metbuild_interface INTERFACE)
add_library(metbuild_objectlib OBJECT ${METBUILD_SOURCES})
add_library(metbuild_static STATIC $<TARGET_OBJECTS:metbuild_objectlib>)
add_library(metbuild SHARED $<TARGET_OBJECTS:metbuild_objectlib>)

find_package( NetCDF REQUIRED )
find_package( PROJ REQUIRED )
find_package( SQLite3 REQUIRED )
find_package( TIFF REQUIRED )
find_package( Boost REQUIRED COMPONENTS iostreams )

set_property(TARGET metbuild_objectlib PROPERTY POSITION_INDEPENDENT_CODE 1)
target_link_libraries(metbuild_static metbuild_interface)
target_link_libraries(metbuild metbuild_interface)

target_compile_features(metbuild_objectlib PRIVATE cxx_std_17)
set_target_properties(metbuild_objectlib PROPERTIES CMAKE_CXX_VISIBILITY_PRESET
                                                    hidden)
set_target_properties(metbuild_objectlib PROPERTIES CMAKE_CXX_INLINES_HIDDEN
                                                    YES)

add_dependencies(metbuild_objectlib eccodes)

set(metbuild_include_list
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${Boost_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/nanoflann
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/fmt-8.1.1/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/eccodes-2.24.2/src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/date_hh
    ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/eccodes/src
    ${NETCDF_INCLUDE_DIRS} ${PROJ_INCLUDE_DIR} ${SQLite3_INCLUDE_DIRS})

target_include_directories(metbuild_objectlib PRIVATE ${metbuild_include_list})

target_link_libraries(metbuild_interface INTERFACE ${NETCDF_LIBRARIES} ${PROJ_LIBRARY} ${SQLite3_LIBRARIES} ${Boost_LIBRARIES} eccodes ${TIFF_LIBRARY_RELEASE})
target_link_libraries(metbuild_static metbuild_interface)
target_link_libraries(metbuild metbuild_interface)

set(HEADER_DEST "${CMAKE_INSTALL_INCLUDEDIR}/metbuild")

write_basic_package_version_file(
  metbuildConfigVersion.cmake
  VERSION ${METGET_VERSION_STRING}
  COMPATIBILITY SameMajorVersion)

install(
  TARGETS metbuild
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT METGET_RUNTIME
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT METGET_RUNTIME
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT METGET_DEVELOPMENT
  PUBLIC_HEADER DESTINATION ${HEADER_DEST} COMPONENT METGET_DEVELOPMENT)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/metbuildConfigVersion.cmake
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake)
install(
  DIRECTORY
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/eccodes-2.24.2/definitions
  DESTINATION ${CMAKE_INSTALL_PREFIX}/share/eccodes)

# ##############################################################################
