cmake_minimum_required(VERSION 3.16)
project(gcu_c_host C)

set(CMAKE_C_STANDARD 11)
enable_testing()

add_library(gcu_core
  ../src/defaults.c
  ../src/domain.c
)
target_include_directories(gcu_core PUBLIC ../include)

add_executable(test_defaults test_defaults.c)
target_link_libraries(test_defaults gcu_core)
add_test(NAME defaults COMMAND test_defaults)

# Convenience: cmake --build build/host --target host_test runs ctest.
# Do not name this target "test" — CMake reserves that name when enable_testing() is on.
add_custom_target(host_test
  COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
  DEPENDS test_defaults
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)
