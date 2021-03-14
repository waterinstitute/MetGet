if(UNIX OR CYGWIN)
  option(METBUILD_BUILD_TESTS OFF "Build test cases")
  enable_testing()
  if(METBUILD_BUILD_TESTS)
    # ...C++ Testing
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/cxx_testcases)

    set(TEST_LIST cxx_test1.cpp)

    foreach(TESTFILE ${TEST_LIST})
      get_filename_component(TESTNAME ${TESTFILE} NAME_WE)
      add_executable(${TESTNAME}
                     ${CMAKE_SOURCE_DIR}/testing/cxx_tests/${TESTFILE})
      add_dependencies(${TESTNAME} metbuild_static)
      target_link_libraries(${TESTNAME} metbuild_static metbuild_interface)
      target_include_directories(
        ${TESTNAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
                            ${CMAKE_CURRENT_SOURCE_DIR}/../../thirdparty/catch2)
      set_target_properties(
        ${TESTNAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                               ${CMAKE_BINARY_DIR}/cxx_testcases)

      add_test(
        NAME TEST_${TESTNAME}
        COMMAND ${CMAKE_BINARY_DIR}/cxx_testcases/${TESTNAME}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
    endforeach()

  endif()
endif()
