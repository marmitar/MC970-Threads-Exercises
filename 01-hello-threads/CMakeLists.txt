cmake_minimum_required(VERSION 3.12)
project(hello_threads C)

# If build type is unspecified, default to Release
if (NOT CMAKE_BUILD_TYPE OR CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build Configuration" FORCE)
endif()

# Enable Link Time Optimizations
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE TRUE CACHE BOOL "Enable LTO in Release")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO TRUE CACHE BOOL "Enable LTO in RelWithDebInfo")

# Set compiler flags
add_compile_options(-pthread)

# 1 if the GCC is the current compiler
set(GCC $<C_COMPILER_ID:GNU>)
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
    if (NOT CMAKE_C_COMPILER_ID MATCHES "Clang")
        message(FATAL_ERROR "Clang is required for optimization reports")
    endif()
    add_compile_options(-Rpass=.* -Rpass-analysis=.* -Rpass-missed=.* -fsave-optimization-record)
endif()

# Create executable
add_executable(hello_threads src/hello_threads.c)
add_executable(hello_threads_solution src/hello_threads_solution.c)

# Link pthreads library
target_link_libraries(hello_threads pthread )
target_link_libraries(hello_threads_solution pthread )


if (EMIT_OPTIMIZATION_REPORTS)
    # Copy the optimization reports to the build directory
    add_custom_target(hello_threads_report ALL
        cp CMakeFiles/*.dir/src/*.opt.yaml .
        DEPENDS hello_threads hello_threads_solution
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
endif()
