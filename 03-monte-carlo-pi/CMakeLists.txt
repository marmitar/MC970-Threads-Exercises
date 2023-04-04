cmake_minimum_required(VERSION 3.12)
project(monte_carlo_pi CXX)

# If build type is unspecified, default to Release
if (NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build Configuration" FORCE)
endif()

# Set C++ standard to C++11
set(CMAKE_CXX_STANDARD 11)

# Enable Link Time Optimizations
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE TRUE CACHE BOOL "Enable LTO in Release")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO TRUE CACHE BOOL "Enable LTO in RelWithDebInfo")

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

# Let the compiler emit reports about optimizations done and missed
set(EMIT_OPTIMIZATION_REPORTS OFF CACHE BOOL "Emit LLVM IR optimization reports")
if (EMIT_OPTIMIZATION_REPORTS)
    if (NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        message(FATAL_ERROR "Clang is required for optimization reports")
    endif()
    add_compile_options(-Rpass=.* -Rpass-analysis=.* -Rpass-missed=.* -fsave-optimization-record)
endif()

# Set number of threads for the solution
set(NUM_THREADS "4" CACHE STRING "Number of threads in concurrent program")
add_compile_definitions(NUM_THREADS=${NUM_THREADS})

# Find Threads library
find_package(Threads REQUIRED)

# Add executable target for serial version
add_executable(monte_carlo_serial src/monte_carlo_serial.cpp)
target_compile_definitions(monte_carlo_serial PRIVATE SERIAL_VERSION)

# Add executable target for parallel version
add_executable(monte_carlo_parallel src/monte_carlo_parallel.cpp)
target_compile_definitions(monte_carlo_parallel PRIVATE PARALLEL_VERSION)

# Add optimized parallel version
add_executable(monte_carlo_optimized src/monte_carlo_optimized.cpp)
target_compile_definitions(monte_carlo_optimized PRIVATE PARALLEL_VERSION)

# Link with Threads library
target_link_libraries(monte_carlo_parallel PRIVATE Threads::Threads)
target_link_libraries(monte_carlo_optimized PRIVATE Threads::Threads)


if (EMIT_OPTIMIZATION_REPORTS)
    # Copy the optimization reports to the build directory
    add_custom_target(monte_carlo_pi_report ALL
        cp CMakeFiles/*.dir/src/*.opt.yaml .
        DEPENDS monte_carlo_serial monte_carlo_parallel monte_carlo_optimized
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
endif()
