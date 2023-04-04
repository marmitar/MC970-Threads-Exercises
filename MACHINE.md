# Hardware and Software Details

Hardware and software details for the machine used to explore and answer the exercises.

## Operating System

```fish
> uname -a
```
```raw
Linux marmis-arch 6.2.8-zen1-1-zen #1 ZEN SMP PREEMPT_DYNAMIC Wed, 22 Mar 2023 22:52:38 +0000 x86_64 GNU/Linux
```

```fish
> cat /proc/sys/kernel/threads-max
```
```raw
126451
```

## Compiler

```fish
> gcc --version
```
```raw
gcc (GCC) 12.2.1 20230201
Copyright (C) 2022 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

```fish
> cmake --version
```
```raw
cmake version 3.26.1

CMake suite maintained and supported by Kitware (kitware.com/cmake).
```

## CPU

```fish
> lscpu
```
```rawArchitecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         43 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  8
  On-line CPU(s) list:   0-7
Vendor ID:               AuthenticAMD
  Model name:            AMD Ryzen 5 1500X Quad-Core Processor
    CPU family:          23
    Model:               1
    Thread(s) per core:  2
    Core(s) per socket:  4
    Socket(s):           1
    Stepping:            1
    BogoMIPS:            7000.17
    Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl nonstop_tsc cpuid extd_apicid aperfmperf
                         rapl pni pclmulqdq monitor ssse3 fma cx16 sse4_1 sse4_2 movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw skinit wdt tce topoext perfctr_core
                         perfctr_nb bpext perfctr_llc mwaitx cpb hw_pstate ssbd ibpb vmmcall fsgsbase bmi1 avx2 smep bmi2 rdseed adx smap clflushopt sha_ni xsaveopt xsavec xgetbv1 clzero irperf xsaveerptr arat npt lbrv svm_lock nrip_save t
                         sc_scale vmcb_clean flushbyasid decodeassists pausefilter pfthreshold avic v_vmsave_vmload vgif overflow_recov succor smca sev
Virtualization features:
  Virtualization:        AMD-V
Caches (sum of all):
  L1d:                   128 KiB (4 instances)
  L1i:                   256 KiB (4 instances)
  L2:                    2 MiB (4 instances)
  L3:                    16 MiB (2 instances)
NUMA:
  NUMA node(s):          1
  NUMA node0 CPU(s):     0-7
Vulnerabilities:
  Itlb multihit:         Not affected
  L1tf:                  Not affected
  Mds:                   Not affected
  Meltdown:              Not affected
  Mmio stale data:       Not affected
  Retbleed:              Vulnerable
  Spec store bypass:     Vulnerable
  Spectre v1:            Vulnerable: __user pointer sanitization and usercopy barriers only; no swapgs barriers
  Spectre v2:            Vulnerable, IBPB: disabled, STIBP: disabled, PBRSB-eIBRS: Not affected
  Srbds:                 Not affected
  Tsx async abort:       Not affected
```

## Memory

```fish
> sudo lshw -class memory
```
```raw
  *-firmware
       description: BIOS
       vendor: American Megatrends Inc.
       physical id: 0
       version: P4.60
       date: 10/20/2022
       size: 64KiB
       capacity: 16MiB
       capabilities: pci upgrade shadowing cdboot bootselect socketedrom edd int13floppy1200 int13floppy720 int13floppy2880 int5printscreen int9keyboard int14serial int17printer acpi usb biosbootspecification uefi
  *-memory
       description: System Memory
       physical id: d
       slot: System board or motherboard
       size: 16GiB
     *-bank:0
          description: [empty]
          product: Unknown
          vendor: Unknown
          physical id: 0
          serial: Unknown
          slot: DIMM 0
     *-bank:1
          description: DIMM DDR4 Synchronous Unbuffered (Unregistered) 3134 MHz (0.3 ns)
          product: KD48GU880-32A160U
          vendor: Unknown
          physical id: 1
          serial: CA583B0C
          slot: DIMM 1
          size: 8GiB
          width: 64 bits
          clock: 3134MHz (0.3ns)
     *-bank:2
          description: [empty]
          product: Unknown
          vendor: Unknown
          physical id: 2
          serial: Unknown
          slot: DIMM 0
     *-bank:3
          description: DIMM DDR4 Synchronous Unbuffered (Unregistered) 3134 MHz (0.3 ns)
          product: KD48GU880-32A160U
          vendor: Unknown
          physical id: 3
          serial: 8F6D3B0C
          slot: DIMM 1
          size: 8GiB
          width: 64 bits
          clock: 3134MHz (0.3ns)
  *-cache:0
       description: L1 cache
       physical id: f
       slot: L1 - Cache
       size: 384KiB
       capacity: 384KiB
       clock: 1GHz (1.0ns)
       capabilities: pipeline-burst internal write-back unified
       configuration: level=1
  *-cache:1
       description: L2 cache
       physical id: 10
       slot: L2 - Cache
       size: 2MiB
       capacity: 2MiB
       clock: 1GHz (1.0ns)
       capabilities: pipeline-burst internal write-back unified
       configuration: level=2
  *-cache:2
       description: L3 cache
       physical id: 11
       slot: L3 - Cache
       size: 16MiB
       capacity: 16MiB
       clock: 1GHz (1.0ns)
       capabilities: pipeline-burst internal write-back unified
       configuration: level=3
```
