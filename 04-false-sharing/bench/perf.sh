#!/bin/bash

INPUT=300000000
THREADS=8

for kind in "sharing" "local"; do
    if [ "$kind" = "sharing" ]; then
        BINARY=build/sum_scalar
    else
        BINARY=build/sum_scalar_solution
    fi

    mkdir -p $kind

    ../$BINARY $INPUT $THREADS > $kind/dry.stdout

    sudo perf c2c record -o $kind/c2c.data -a ../$BINARY $INPUT $THREADS > $kind/c2c.stdout
    sudo perf mem record -o $kind/mem.data -a ../$BINARY $INPUT $THREADS > $kind/mem.stdout
    sudo perf stat -e cache-misses -a record -o $kind/stat.data ../$BINARY $INPUT $THREADS > $kind/stat.stdout

    sudo chown $(whoami) $kind/*.data
    perf c2c report -i $kind/c2c.data --stdio > $kind/c2c.txt
    perf mem report -i $kind/mem.data --stdio > $kind/mem.txt
    perf stat report -i $kind/stat.data &> $kind/stat.txt
done
