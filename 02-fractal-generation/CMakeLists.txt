cmake_minimum_required(VERSION 3.12)
project(mandelbrot CXX)

# If build type is unspecified, default to Release
if (NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build Configuration" FORCE)
endif()

# Set C++ standard to C++11
set(CMAKE_CXX_STANDARD 11)

# Set compiler flags
add_compile_options(-m64 -fPIC)

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

# Find Threads library and libm
find_package(Threads REQUIRED)
find_library(Math m REQUIRED)

# Create executable
add_executable(${PROJECT_NAME})

# Add sources to executable
set(OBJDIR src)
target_include_directories(${PROJECT_NAME} PRIVATE ${OBJDIR})
target_sources(${PROJECT_NAME}
    PRIVATE
        ${OBJDIR}/main.cpp
        ${OBJDIR}/mandelbrotSerial.cpp
        ${OBJDIR}/mandelbrotThread.cpp
        ${OBJDIR}/ppm.cpp
)

# Link Threads and math library
target_link_libraries(${PROJECT_NAME} PRIVATE Threads::Threads ${Math})


if (EMIT_OPTIMIZATION_REPORTS)
    # Copy the optimization reports to the build directory
    add_custom_target(mandelbrot_report ALL
        cp CMakeFiles/*.dir/src/*.opt.yaml .
        DEPENDS ${PROJECT_NAME}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
endif()
