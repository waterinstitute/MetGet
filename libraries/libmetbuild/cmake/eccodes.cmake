# ##############################################################################
# ECCODES GRIB API
# ##############################################################################
set(ENABLE_FORTRAN
    OFF
    CACHE BOOL "Enable Fortran functionality in eccodes")
set(ENABLE_PYTHON
    OFF
    CACHE BOOL "Enable Python functionality in eccodes")
set(ENABLE_PRODUCT_BUFR
    OFF
    CACHE BOOL "Enable BUFR")
set(BUILD_SHARED_LIBS
    OFF
    CACHE BOOL "Enable building shared libraries")

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

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/eccodes-2.18.0
                 ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/eccodes EXCLUDE_FROM_ALL)
# ##############################################################################
