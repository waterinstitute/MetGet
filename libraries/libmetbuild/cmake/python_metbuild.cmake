# ##############################################################################
# Python MetBuild Library
# ##############################################################################
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/python_metbuild_wrap.cxx
  COMMAND
    ${SWIG_EXECUTABLE} -outdir ${CMAKE_CURRENT_BINARY_DIR} -c++ -python
    ${PYTHONFLAG} -I${CMAKE_CURRENT_SOURCE_DIR}/src -I${PYTHON_INCLUDE_PATH}
    ${SWIG_GDAL_FLAG} -o
    ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/python_metbuild_wrap.cxx
    ${CMAKE_CURRENT_SOURCE_DIR}/swig/metbuild.i
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Generating SWIG interface to Python...")

add_library(pymetbuild SHARED
            ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/python_metbuild_wrap.cxx)
target_include_directories(
  pymetbuild PRIVATE ${Python3_INCLUDE_DIRS}
                     ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(pymetbuild metbuild_static)
if(APPLE)
  target_link_libraries(pymetbuild Python3::Module)
endif(APPLE)
set_target_properties(pymetbuild PROPERTIES PREFIX "_")
set_target_properties(pymetbuild PROPERTIES INSTALL_NAME_DIR "metbuild")
set_property(
  DIRECTORY
  APPEND
  PROPERTY ADDITIONAL_MAKE_CLEAN_FILES pymetbuild.py
           CMakeFiles/python_metbuild_wrap.cxx)

add_dependencies(pymetbuild metbuild)

set_target_properties(pymetbuild PROPERTIES LIBRARY_OUTPUT_DIRECTORY
                                            ${CMAKE_CURRENT_BINARY_DIR})
install(TARGETS pymetbuild LIBRARY DESTINATION ${PYTHON_INSTALL_DIRECTORY})

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/pymetbuild.py
        DESTINATION ${PYTHON_INSTALL_DIRECTORY})

if(APPLE)
  set_target_properties(pymetbuild PROPERTIES SUFFIX ".so")
endif(APPLE)
# ##############################################################################
