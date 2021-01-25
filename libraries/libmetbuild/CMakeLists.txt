# ##############################################################################
# MetBuild Cmake Build System
#
# Written By: Zach Cobell Contact: zcobell@thewaterinstitute.org
# ##############################################################################

# ...Set the default build type
if(DEFINED CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE
      ${CMAKE_BUILD_TYPE}
      CACHE STRING "Choose the type of
        build, options are: None(CMAKE_CXX_FLAGS or CMAKE_C_FLAGS used) Debug
        Release RelWithDebInfo MinSizeRel.")
else()
  set(CMAKE_BUILD_TYPE
      Release
      CACHE STRING "Choose the type of build,
        options are: None(CMAKE_CXX_FLAGS or CMAKE_C_FLAGS used) Debug Release
        RelWithDebInfo MinSizeRel.")
endif()

cmake_minimum_required(VERSION 3.0)
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
cmake_policy(SET CMP0048 NEW)
project(
  MetGet
  LANGUAGES C CXX
  VERSION 0.0.1)
set(CMAKE_CXX_STANDARD 14)

include(CheckIncludeFiles)
include(CheckLibraryExists)
include(CheckFunctionExists)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

mark_as_advanced(
  CLEAR
  CMAKE_C_COMPILER
  CMAKE_CXX_COMPILER
  CMAKE_C_CFLAGS
  CMAKE_CXX_FLAGS
  CMAKE_C_FLAGS_DEBUG
  CMAKE_C_FLAGS_RELEASE
  CMAKE_CXX_FLAGS_DEBUG
  CMAKE_CXX_FLAGS_RELEASE)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/python.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/netcdf_check.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/eccodes.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/libmetbuild.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/python_metbuild.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/test_cases.cmake)
