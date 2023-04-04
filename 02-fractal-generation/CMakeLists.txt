cmake_minimum_required(VERSION 3.12)
project(mandelbrot CXX)

# If build type is unspecified, default to Release
if (NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build Configuration" FORCE)
endif()

set(CMAKE_CXX_STANDARD 11)
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

set(APP_NAME mandelbrot)
set(OBJDIR src)

add_executable(${APP_NAME} "")

target_include_directories(${APP_NAME} PRIVATE ${OBJDIR})

target_sources(${APP_NAME}
    PRIVATE
        ${OBJDIR}/main.cpp
        ${OBJDIR}/mandelbrotSerial.cpp
        ${OBJDIR}/mandelbrotThread.cpp
        ${OBJDIR}/ppm.cpp
)

target_link_libraries(${APP_NAME} PRIVATE pthread m)
