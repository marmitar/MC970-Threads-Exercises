# Solution and Answers

The specific hardware and software used for this exercise can be found at [MACHINE.md](../MACHINE.md).

## Disabling Optimizations

The hot loop in the `sum(...)` function may be transformed by an optimizing compiler, negating the performance penalty expected in this exercise. GCC specifically completely removes the loop in `-O3`, changing it to a single conditional store. In `-O1`, GCC keeps the loop, but still does a single store at `psum[..]` after the loop. Both optimizations resolves the false-sharing in `sum_scalar`. To bypass this, I've updated code with a `step()` function that has interprocedural optimizations (IPA) disabled:

```c
static __attribute__((noipa))
unsigned long step(void) {
    return 2;
}

void *sum(void *p) {
    // ...
    for (unsigned long i = start; i < end; i++) {
        psum[myid] += step();
    }
    // ...
}
```

## Detecting False-Sharing

To identify where the false-sharing is happening, a very useful tool is `perf mem`, but it only works on modern Intel microprocessors. My [machine](../MACHINE.md) has an AMD Ryzen chip, so I had to run it on another machine. The full results for the false-sharing code can be found at [sharing/mem.txt](bench/sharing/mem.txt), but the first few lines are shown below:

```raw
# Overhead       Samples  Local Weight  Memory access             Symbol                                 Shared Object          Data Symbol                                Data Object              Snoop         TLB access              Locked  Blocked     Local INSTR Latency
# ........  ............  ............  ........................  .....................................  .....................  .........................................  .......................  ............  ......................  ......  ..........  ...................
#
     1.44%           149  32            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x8                               sum_scalar               None          L1 or L2 hit            No       N/A        0
     1.35%           140  32            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x38                              sum_scalar               None          L1 or L2 hit            No       N/A        0
     1.22%           123  33            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x38                              sum_scalar               None          L1 or L2 hit            No       N/A        0
     1.15%           119  32            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x10                              sum_scalar               None          L1 or L2 hit            No       N/A        0
     1.03%           107  32            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x28                              sum_scalar               None          L1 or L2 hit            No       N/A        0
     0.94%            89  35            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x8                               sum_scalar               None          L1 or L2 hit            No       N/A        0
     0.92%            92  33            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x8                               sum_scalar               None          L1 or L2 hit            No       N/A        0
     0.91%            86  35            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x10                              sum_scalar               None          L1 or L2 hit            No       N/A        0
     0.84%            80  35            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x38                              sum_scalar               None          L1 or L2 hit            No       N/A        0
     0.80%            83  32            L1 or L1 hit              [.] sum                                sum_scalar             [.] psum+0x30                              sum_scalar               None          L1 or L2 hit            No       N/A        0
```

The table shows that most of the memory overhead in the `sum(...)` function happens with the `psum` array. This heavily implies that the array is the culprit for the performance loss.

## No-Sharing Solution

One of the proposed solutions for false-sharing in *An Introduction to Parallel Programming (Pacheco, Malensek)* is by using a private storage and updating the shared storage after the loop. Basically the same GCC does with its optimization flags. The implemented solution ([sum_scalar_solution.c](src/sum_scalar_solution.c)) follows the same principle, but removes the shared array completely.


## Improvements

### Execution Time

With `n = 300_000_000`, the code went from 576 ms ([sharing/dry.stdout](bench/sharing/dry.stdout)) to 93.5 ms ([local/dry.stdout](bench/local/dry.stdout)) on the Intel machine, a 6x speedup. On my AMD machine, the change is even more pronounced, going from 765 ms to only 62.9 ms (12x speedup).

### Cache Misses

The amount of cache misses also improved a considerable amount when measured with `perf stat -e cache-misses`. It went from 131.084 misses ([sharing/stat.txt](bench/sharing/stat.txt)) to only 50.059 ([local/stat.txt](bench/local/stat.txt)) in the no-sharing solution.
