from __future__ import annotations
from typing import Any, ClassVar, Iterator, final

from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree

import os
import re
import tempfile
import subprocess
import sys

from tqdm import trange


# Path and directory of this script
SCRIPTPATH = Path(sys.argv[0]).resolve(strict=True)
SCRIPTDIR = SCRIPTPATH.parent.resolve(strict=True)

# Path for the 'mandelbrot' executablel, relative to the current dir
BINARY = Path('build/mandelbrot').resolve(strict=True)

# OS directory for temporary files, usually placed in memory
TMPDIR = Path('/tmp').resolve(strict=True)

@contextmanager
def chdir(path: Path) -> Iterator[str]:
    """Changes current directory on `__enter__` and restores on `__exit__`."""
    curdir = Path('.').resolve(strict=True)
    try:
        os.chdir(path)
        yield curdir
    finally:
        os.chdir(curdir)

@contextmanager
def tempdir(*, parent: Path = TMPDIR) -> Iterator[str]:
    """Creates a temporary directory and `chdir` to it, removing everything on `__exit__`."""
    dirpath = tempfile.mkdtemp(dir=parent)
    try:
        with chdir(dirpath):
            yield dirpath
    finally:
        rmtree(dirpath, ignore_errors=True)


@final
@dataclass(frozen=True)
class Mandelbrot:
    """Inputs and outputs of a single execution of 'mandelbrot'."""

    serial: float
    """Time in ms to run the serial implementation."""
    thread: float
    """Time in ms to run the threaded implementation."""
    speedup: float
    """`self.serial / self.thread`, taken from the program output."""
    nthreads: int
    """Number of threads used in the threaded execution."""

    TIME_RE: ClassVar[re.Pattern[str]] = \
        re.compile('\[mandelbrot (?P<name>\w+)\]:\s+\[(?P<time>\d*.\d*)\]\s+ms')
    """Regular Expression to extract the execution times from the program output."""
    CONFIG_RE: ClassVar[re.Pattern[str]] = \
        re.compile('\((?P<speedup>\d*.\d*)x speedup from (?P<nthreads>\d+) threads\)')
    """Regular Expression to extract speedup and number of threads from the program output."""

    @classmethod
    def parse(cls, execution: str) -> Mandelbrot:
        times: dict[Any, float] = {}
        for match in cls.TIME_RE.finditer(execution):
            name = match.group('name')
            time = match.group('time')
            assert name not in times
            times[name] = float(time)

        match, = cls.CONFIG_RE.finditer(execution)
        speedup = float(match.group('speedup'))
        nthreads = int(match.group('nthreads'))

        return cls(times['serial'], times['thread'], speedup, nthreads)

    @classmethod
    def run(cls, *, threads: int, view: int) -> Mandelbrot:
        assert threads > 0

        cmd = BINARY, '--threads', f'{threads:d}', '--view', f'{view:d}'
        proc = subprocess.run(cmd, capture_output=True, check=True, text=True, input='')
        results = cls.parse(proc.stdout)

        assert results.nthreads == threads
        return results

    @classmethod
    def csv_header(cls) -> str:
        KEYS = ('serial', 'thread', 'speedup', 'nthreads')
        for key in KEYS:
            assert key in cls.__dataclass_fields__
        return ','.join(KEYS)

    def to_csv(self) -> str:
        values = (
            f'{self.serial:.3f}',
            f'{self.thread:.3f}',
            f'{self.speedup:.2f}',
            f'{self.nthreads:d}',
        )
        return ','.join(values)


@tempdir()
def batch_exec(*, repeats: int) -> Iterator[Mandelbrot]:
    MAX_THREADS = 32
    VIEW = 1

    """Run `repeats` batch executions of `mandelbrot` in a temporary directory."""
    for _ in trange(repeats, desc='Repetition'):
        for n in trange(1, MAX_THREADS + 1, desc='Threads'):
            yield Mandelbrot.run(threads=n, view=VIEW)


@chdir(SCRIPTDIR)
def main(repetitions: int = 1):
    LATEST = 'latest.csv'

    with open(f'{datetime.now()}.csv', 'wt') as csv:
        # symlink most recent csv to latest.csv
        try:
            os.unlink(LATEST)
        except FileNotFoundError:
            pass
        finally:
            os.symlink(csv.name, LATEST)

        # then run mandelbrot and save outputs in csv
        print(Mandelbrot.csv_header(), file=csv, flush=True)
        for timing in batch_exec(repeats=repetitions):
            print(timing.to_csv(), file=csv, flush=True)


if __name__ == "__main__":
    assert len(sys.argv) == 2
    REPEATS = int(sys.argv[1])
    assert REPEATS > 0

    main(REPEATS)
