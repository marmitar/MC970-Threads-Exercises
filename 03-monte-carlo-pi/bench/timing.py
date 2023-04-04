from __future__ import annotations
from typing import ClassVar, Iterable, Iterator, TextIO, final

from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from shutil import rmtree
from time import time

import math
import os
import re
import subprocess
import sys
import tempfile

from tqdm import tqdm, trange


# Path and directory of this script
SCRIPTPATH = Path(sys.argv[0]).resolve(strict=True)
SCRIPTDIR = SCRIPTPATH.parent.resolve(strict=True)

# Path for sources and output binaries
SRCDIR = SCRIPTDIR.parent.resolve(strict=True)
CMAKE_CACHE = Path('CMakeCache.txt')

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


def exec(command: str, *args: str):
    cmd = (command, *args)

    start = time()
    proc = subprocess.run(cmd, capture_output=True, check=True, text=True, input='')
    end = time()

    elapsed = end - start
    return proc.stdout, elapsed


@final
@unique
class Executable(str, Enum):
    SERIAL    = 'monte_carlo_serial'
    PARALLEL  = 'monte_carlo_parallel'
    OPTIMIZED = 'monte_carlo_optimized'

    @property
    def path(self) -> Path:
        return Path(self.value).resolve(strict=True)

    @property
    def id(self) -> int:
        for index, program in enumerate(Executable):
            if program == self:
                return index

        raise ValueError(self)

    def run(self) -> tuple[str, float]:
        return exec(str(self.path))

@final
@dataclass(frozen=True)
class Execution:
    program: Executable
    nthreads: int
    time: float
    count: int
    pi: float

    @property
    def error(self) -> float:
        return abs(self.pi - math.pi)

    PI_RE: ClassVar[re.Pattern[str]] = \
        re.compile('Used (?P<count>\d+) points to estimate pi: (?P<pi>\d*.\d*)')

    @classmethod
    def parse(cls, output: str, program: Executable, nthreads: int, time: float) -> Execution:
        match, = cls.PI_RE.finditer(output)
        count = int(match.group('count'))
        pi = float(match.group('pi'))
        return Execution(program, nthreads, time, count, pi)

    @classmethod
    def csv_header(cls) -> str:
        KEYS = ('program', 'nthreads', 'time', 'count', 'pi')
        for key in KEYS:
            assert key in cls.__dataclass_fields__
        return ','.join(KEYS)

    def to_csv(self) -> str:
        values = (
            f'{self.program:s}',
            f'{self.nthreads:02d}',
            f'{self.time:.3f}',
            f'{self.count:d}',
            f'{self.pi:.6f}',
        )
        return ','.join(values)

@final
class MonteCarlo:
    BEST_OF = 5
    BATCH_SIZE = 5

    NUM_THREADS_RE: ClassVar[re.Pattern[str]] = \
        re.compile('^NUM_THREADS:\w+=(?P<nthreads>\d+)$')

    @classmethod
    @property
    def nthreads(cls) -> int | None:
        if not CMAKE_CACHE.is_file():
            return None

        with CMAKE_CACHE.open('rt') as cache:
            for line in cache:
                for match in cls.NUM_THREADS_RE.finditer(line):
                    return int(match.group('nthreads'))

        return None

    @classmethod
    def make(cls, nthreads: int) -> None:
        assert nthreads > 0
        exec('cmake', '-D', f'NUM_THREADS={nthreads:d}', SRCDIR)
        exec('make')
        assert cls.nthreads == nthreads

    @classmethod
    def run(cls, program: Executable, nthreads: int) -> Execution:
        if cls.nthreads != nthreads:
            cls.make(nthreads)

        results = (program.run() for _ in range(cls.BEST_OF))
        outpu, time = min(results, key=lambda r: r[1])
        return Execution.parse(outpu, program, cls.nthreads, time)

    @classmethod
    def batch(cls, program: Executable, nthreads: int) -> Execution:
        results = [cls.run(program, nthreads) for _ in trange(cls.BATCH_SIZE, desc='Run')]

        assert all(r.program == program for r in results)
        assert all(r.nthreads == nthreads for r in results)
        avg_time = sum(r.time for r in results) / len(results)
        avg_count = sum(r.count for r in results) / len(results)
        avg_pi = sum(r.pi for r in results) / len(results)

        return Execution(program, nthreads, avg_time, int(avg_count), avg_pi)


def batch_exec():
    NTHREDS = (1, 2, 4, 6, 8, 12, 16, 24, 32)
    for nthreads in tqdm(NTHREDS, desc='Num. Threads'):
        for program in tqdm(Executable, desc='Binary'):
            yield MonteCarlo.batch(program, nthreads)


@final
class ResultsCSV:
    def __init__(self, file: TextIO):
        print(Execution.csv_header(), file=file, flush=True)
        self.results: list[Execution] = []
        self.csv = file

    def insert(self, execution: Execution):
        print(execution.to_csv(), file=self.csv, flush=True)
        self.results.append(execution)

    @contextmanager
    @staticmethod
    def open(path: Path) -> Iterator[ResultsCSV]:
        with open(path, 'wt') as csv:
            yield ResultsCSV(csv)


@tempdir()
def run():
    OUTPUT = SCRIPTDIR.joinpath('results.csv')

    # write the csv while results are coming
    with ResultsCSV.open(OUTPUT) as csv:
        for result in batch_exec():
            csv.insert(result)
        results = csv.results

    # then rewrite the results sorted by program
    with ResultsCSV.open(OUTPUT) as csv:
        sorted_results = sorted(results, key=lambda r: (r.program.id, r.nthreads))
        for result in sorted_results:
            csv.insert(result)


if __name__ == "__main__":
    run()
