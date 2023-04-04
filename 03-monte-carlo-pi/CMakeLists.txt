cmake_minimum_required(VERSION 3.12)
project(monte_carlo_pi CXX)

# If build type is unspecified, default to Release
if (NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build Configuration" FORCE)
endif()

# Set C++ standard to C++11
set(CMAKE_CXX_STANDARD 11)

# 1 if the GCC is the current compiler
set(GCC $<CXX_COMPILER_ID:GNU>)
# Set compiler warnings
add_compile_options(
    -Wall -Wextra -Wpedantic
    # String and formatting
    -Wformat=2 $<${GCC}:-Wformat-truncation=2> $<${GCC}:-Wformat-overflow=2> $<${GCC}:-Wstringop-overflow=4>
    # Implicit casts
    -Wconversion -Wsign-conversion $<${GCC}:-Wformat-signedness>
    # Variadic macros should not be empty, but most compiler accept it anyway,
    # so it is okay to disable this warning
    -Wno-gnu-zero-variadic-macro-arguments
)
add_compile_definitions($<$<CONFIG:Release>:_FORTIFY_SOURCE=1>)
add_compile_definitions($<$<CONFIG:RelWithDebInfo>:_FORTIFY_SOURCE=3>)

# Find Threads library
find_package(Threads REQUIRED)

# Add executable target for serial version
add_executable(monte_carlo_serial src/monte_carlo_serial.cpp)
target_compile_definitions(monte_carlo_serial PRIVATE SERIAL_VERSION)

# Add executable target for parallel version
add_executable(monte_carlo_parallel src/monte_carlo_parallel.cpp)
target_compile_definitions(monte_carlo_parallel PRIVATE PARALLEL_VERSION)

# Link with Threads library
target_link_libraries(monte_carlo_parallel Threads::Threads)
