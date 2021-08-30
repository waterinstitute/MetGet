# ##############################################################################
# libmetbuild
# ##############################################################################

set(METBUILD_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Date.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Grib.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Kdtree.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/KdtreePrivate.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Meteorology.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/WindGrid.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/NcFile.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/Logging.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/WindData.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/OwiAscii.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/OwiNetcdf.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/OwiAsciiDomain.cpp)

add_library(metbuild_interface INTERFACE)
add_library(metbuild_objectlib OBJECT ${METBUILD_SOURCES})
add_library(metbuild_static STATIC $<TARGET_OBJECTS:metbuild_objectlib>)
add_library(metbuild SHARED $<TARGET_OBJECTS:metbuild_objectlib>)

set_property(TARGET metbuild_objectlib PROPERTY POSITION_INDEPENDENT_CODE 1)
target_link_libraries(metbuild_static metbuild_interface)
target_link_libraries(metbuild metbuild_interface)

target_compile_features(metbuild_objectlib PRIVATE cxx_std_14)
set_target_properties(metbuild_objectlib PROPERTIES CMAKE_CXX_VISIBILITY_PRESET
                                                    hidden)
set_target_properties(metbuild_objectlib PROPERTIES CMAKE_CXX_INLINES_HIDDEN
                                                    YES)

add_dependencies(metbuild_objectlib eccodes)

set(metbuild_include_list
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/boost_1_75_0
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/nanoflann
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/eccodes-2.18.0/src
    ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/date_hh
    ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/eccodes/src
    ${NETCDF_INCLUDE_DIRS})

target_include_directories(metbuild_objectlib PRIVATE ${metbuild_include_list})

target_link_libraries(metbuild_interface INTERFACE ${NETCDF_LIBRARIES} eccodes)
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
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/eccodes-2.18.0/definitions
  DESTINATION ${CMAKE_INSTALL_PREFIX}/share/eccodes)

# ##############################################################################
