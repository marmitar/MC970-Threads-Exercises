from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPTDIR = Path(sys.argv[0]).parent.resolve(strict=True)
OUTPUT = SCRIPTDIR.joinpath('results.csv')

if __name__ == "__main__":
    df = pd.read_csv(OUTPUT)

    # df['error'] = np.abs(df['pi'] - np.pi)
    # fmt = (None, None, '.3f', None, '.6f', '1.3e')
    # print(df.to_markdown(index=False, floatfmt=fmt))

    for program, group in df.groupby('program'):
        error = np.mean(np.abs(group['pi'] - np.pi))
        print(f'{program:10s} {error:.6f}')
