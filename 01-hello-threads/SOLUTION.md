# Solution and Answers

The specific hardware and software used for this exercise can be found at [MACHINE.md](../MACHINE.md).

## Safety

The POSIX function `sleep(...)` may be thread-unsafe, as it could be implemented using `SIGALARM`. More details can be found at [the man page](https://man7.org/linux/man-pages/man3/sleep.3.html#NOTES). For Linux specifically, the implementation is guaranteed to be thread-safe.

## Timings

### Sequential

```fish
> time build/hello_threads > /dev/null

________________________________________________________
Executed in   15.00 secs      fish           external
   usr time  462.00 micros    0.00 micros  462.00 micros
   sys time  247.00 micros  247.00 micros    0.00 micros

```

### Concurrent

```fish
> time build/hello_threads_solution > /dev/null

________________________________________________________
Executed in    3.00 secs      fish           external
   usr time  132.00 micros  132.00 micros    0.00 micros
   sys time  875.00 micros   79.00 micros  796.00 micros

```

## 1. Can your program create more threads than cores in the CPU?

A program can definitely use more threads than CPU cores. Operating Systems set a numerical limit for threads (126451 for my machine), but the program may run out of memory before reaching that limit. Yet, at least a few hundred threads should be spawnnable. Here is an example using more thread than physical cores.

<details>
  <summary>Example with 35 threads in my 4-core machine.</summary>

```fish
> cmake -B build -D NUM_THREADS=35 .
> make -C build
> time build/hello_threads_solution
Creating thread #0
Creating thread #1
Hello Worlds from thread #0!
Creating thread #2
Hello Worlds from thread #1!
Creating thread #3
Hello Worlds from thread #2!
Creating thread #4
Hello Worlds from thread #3!
Creating thread #5
Hello Worlds from thread #4!
Creating thread #6
Hello Worlds from thread #5!
Creating thread #7
Hello Worlds from thread #6!
Creating thread #8
Hello Worlds from thread #7!
Creating thread #9
Hello Worlds from thread #8!
Creating thread #10
Hello Worlds from thread #9!
Creating thread #11
Hello Worlds from thread #10!
Creating thread #12
Hello Worlds from thread #11!
Creating thread #13
Hello Worlds from thread #12!
Creating thread #14
Hello Worlds from thread #13!
Creating thread #15
Hello Worlds from thread #14!
Creating thread #16
Hello Worlds from thread #15!
Creating thread #17
Hello Worlds from thread #16!
Creating thread #18
Hello Worlds from thread #17!
Creating thread #19
Hello Worlds from thread #18!
Creating thread #20
Hello Worlds from thread #19!
Creating thread #21
Hello Worlds from thread #20!
Creating thread #22
Hello Worlds from thread #21!
Creating thread #23
Hello Worlds from thread #22!
Creating thread #24
Hello Worlds from thread #23!
Creating thread #25
Hello Worlds from thread #24!
Creating thread #26
Hello Worlds from thread #25!
Creating thread #27
Hello Worlds from thread #26!
Creating thread #28
Hello Worlds from thread #27!
Creating thread #29
Hello Worlds from thread #28!
Creating thread #30
Hello Worlds from thread #29!
Creating thread #31
Hello Worlds from thread #30!
Creating thread #32
Hello Worlds from thread #31!
Creating thread #33
Hello Worlds from thread #32!
Creating thread #34
Hello Worlds from thread #33!
Hello Worlds from thread #34!
Goodbye from thread #3!
Goodbye from thread #4!
Goodbye from thread #1!
Goodbye from thread #2!
Goodbye from thread #5!
Goodbye from thread #6!
Goodbye from thread #7!
Goodbye from thread #9!
Goodbye from thread #8!
Goodbye from thread #10!
Goodbye from thread #11!
Goodbye from thread #12!
Goodbye from thread #13!
Goodbye from thread #14!
Goodbye from thread #0!
Goodbye from thread #15!
Goodbye from thread #16!
Goodbye from thread #17!
Goodbye from thread #18!
Goodbye from thread #19!
Goodbye from thread #20!
Goodbye from thread #24!
Goodbye from thread #21!
Goodbye from thread #23!
Goodbye from thread #22!
Goodbye from thread #25!
Goodbye from thread #27!
Goodbye from thread #26!
Goodbye from thread #28!
Goodbye from thread #30!
Goodbye from thread #31!
Goodbye from thread #29!
Goodbye from thread #32!
Goodbye from thread #33!
Goodbye from thread #34!

________________________________________________________
Executed in    3.00 secs      fish           external
   usr time    0.12 millis  122.00 micros    0.00 millis
   sys time    2.32 millis   89.00 micros    2.23 millis

```

</details>

## Answers

### 2. What can the function `pthread_create(...)` return? Why?

According to [the man page](https://man7.org/linux/man-pages/man3/pthread_create.3.html), `pthread_create(...)` should return 0 or the thread is created and an error number if it can't be created for some reason. Common errors are related to insufficient resources like memory, the OS limit was reached, invalid attributes or insufficient permissions for the running process.

### 3. What is the `pthread_join(...)` function for?

`pthread_join(...)` waits for the specified thread to terminate. The exit status of the thread may be returned in a location passed to `pthread_join(..., location)`. More details can be found at [the man page](https://man7.org/linux/man-pages/man3/pthread_join.3.html).

### 4. In what order are the threads executed?

Threads can run in any order. You can change the thread's priority to increase the likelihood that a specific thread will be run before the others, but it still depends on the current scheduler and the OS to choose which thread to run, if any.
