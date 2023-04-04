cmake_minimum_required(VERSION 3.12)
project(sum-scalar C)

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

# Create executable
add_executable(sum_scalar src/sum_scalar.c)
add_executable(sum_scalar_solution src/sum_scalar_solution.c)

# Link pthreads library
target_link_libraries(sum_scalar pthread)
target_link_libraries(sum_scalar_solution pthread)
