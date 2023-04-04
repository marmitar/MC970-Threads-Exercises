# Solution and Answers

The specific hardware and software used for this exercise can be found at [MACHINE.md](../MACHINE.md).

## Implementation

The parallel version was implemented in a thread-safe manner, but it isn't very performant. The biggest culprit for that is the `n_point++` operation in `calculate_pi(..)`. I assume the solution had to mantain that operation because of the comment following it, `// count every try`.

Thread safety was achieved by using `std::atomic` and `thread_local` variables.

### Optimized Parallel Version

For the sake of completeness, I implemented another parallel version ([`monte_carlo_optimized.cpp`](src/monte_carlo_optimized.cpp)) without this restriction. Moving the `n_points++` operation out of the hot loop seems to have a 5x speedup impact. Another noticeable performance gain was from turning the `thread_local std::mt19937 gen` from `random_number(..)` into a local variable in `calculate_pi(..)`, with an approximate 1.1x speedup.

There is also the change from `std::mt19937` to `std::mt19937_64` which resulted in a 1.2x speedup for `NUM_THREADS=1` and even more for more threads. This is likely because `std::mt19937` yields values with 32 bits of "entropy", so it requires two `gen()` calls to build a single `double`, while `std::mt19937_64` needs only a `gen()` call. This change makes `monte_carlo_optimized.cpp` arguably less comparable to `monte_carlo_parallel.cpp`, but it is a nice improvement that couldn't be left out.

## Timings

The code was benchmarked with another python script ([timing.py](bench/timing.py)) that takes the best time of 5 consecutive runs, repeats this process 5 times and output the average of these best times. The measured values are as follows:

| Binary                | `NUM_THREADS` | Time[^detail] | `n_points` | $\pi_\text{calculated}$ | $\left\lvert\pi_\text{calculated} - \pi\right\rvert$ |
| :-------------------  | ------------: | ------------: | :--------: | :-------: | :-------: |
| monte_carlo_serial    |             1 |         1.016 |   30000000 |  3.141748 | 1.553e-04 |
| monte_carlo_serial    |             2 |         1.008 |   30000000 |  3.141414 | 1.787e-04 |
| monte_carlo_serial    |             4 |         1.007 |   30000000 |  3.141546 | 4.665e-05 |
| monte_carlo_serial    |             6 |         1.007 |   30000000 |  3.141768 | 1.753e-04 |
| monte_carlo_serial    |             8 |         1.007 |   30000000 |  3.141576 | 1.665e-05 |
| monte_carlo_serial    |            12 |         1.007 |   30000000 |  3.141710 | 1.173e-04 |
| monte_carlo_serial    |            16 |         1.008 |   30000000 |  3.141590 | 2.654e-06 |
| monte_carlo_serial    |            24 |         1.006 |   30000000 |  3.141512 | 8.065e-05 |
| monte_carlo_serial    |            32 |         1.007 |   30000000 |  3.142006 | 4.133e-04 |
| monte_carlo_parallel  |             1 |         1.048 |   30000000 |  3.141706 | 1.133e-04 |
| monte_carlo_parallel  |             2 |         0.690 |   30000000 |  3.141584 | 8.654e-06 |
| monte_carlo_parallel  |             4 |         0.920 |   30000000 |  3.141684 | 9.135e-05 |
| monte_carlo_parallel  |             6 |         0.740 |   30000000 |  3.141594 | 1.346e-06 |
| monte_carlo_parallel  |             8 |         0.651 |   30000000 |  3.141568 | 2.465e-05 |
| monte_carlo_parallel  |            12 |         0.616 |   30000000 |  3.141794 | 2.013e-04 |
| monte_carlo_parallel  |            16 |         0.617 |   30000000 |  3.141784 | 1.913e-04 |
| monte_carlo_parallel  |            24 |         0.601 |   30000000 |  3.141698 | 1.053e-04 |
| monte_carlo_parallel  |            32 |         0.606 |   30000000 |  3.141672 | 7.935e-05 |
| monte_carlo_optimized |             1 |         0.764 |   30000000 |  3.141464 | 1.287e-04 |
| monte_carlo_optimized |             2 |         0.386 |   30000000 |  3.141466 | 1.267e-04 |
| monte_carlo_optimized |             4 |         0.206 |   30000000 |  3.141620 | 2.735e-05 |
| monte_carlo_optimized |             6 |         0.168 |   30000000 |  3.141774 | 1.813e-04 |
| monte_carlo_optimized |             8 |         0.129 |   30000000 |  3.141506 | 8.665e-05 |
| monte_carlo_optimized |            12 |         0.143 |   30000000 |  3.141684 | 9.135e-05 |
| monte_carlo_optimized |            16 |         0.135 |   30000000 |  3.141504 | 8.865e-05 |
| monte_carlo_optimized |            24 |         0.131 |   30000000 |  3.141578 | 1.465e-05 |
| monte_carlo_optimized |            32 |         0.130 |   30000000 |  3.141576 | 1.665e-05 |

[^detail]: The data was collected with the computer in a somewhat idle state, outside a graphical environment and with a minimal amount of services running in the background.

## Answers

### 1. What is the optimal number of threads to use on your computer?

Either 2 or 8 threads could be considered optimal for the parallel version, since the speedup was basically stagnant after 8 threads. Still, the speedup was only 1.5x, so the parallel version may not be worth it. The optimized version has an almost linear speedup of 7.81x at 8 threads.

### 2. How does the accuracy of the approximation change with the number of threads?

Assuming the program is correct (i.e. no data race is present), then accuracy should be the same. However, looking at the error values ($\left\lvert\pi_\text{calculated} - \pi\right\rvert$), the serial versions tend to be slightly closer to the expected value (the data shown above points to this, but multiple other tests also have this characteristic), with an average error of 0.000085 for `monte_carlo_serial` versus 0.000091 for `monte_carlo_parallel` (0.000132 for `monte_carlo_optimized`). My guess is that it has to do with the pseudo-random number generator used (or the multiple instances of it), but how it causes this is beyond me.

### 3. Is there any race condition on the resulting data?

No, I've changed the shared variables (`count` and `n_point`) to `std::atomic` so that data races can't happen there. To aliviate the performance cost of these atomic operations, I used `std::memory_order_relaxed`.

Another variable prone to data races is the `static std::mt19937` PRNG stored in `random_number(...)`. The solution for the PRNG could be either a `std::mutex` to prevent concurrent modifications to its internal state, or a `thread_local std::mt19937` so that each thread has its own PRNG. The mutex solution is extremely inneficient, so I went with the second option.
