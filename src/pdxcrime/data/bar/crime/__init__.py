import io
import pkgutil

import pandas as pd

import pyarrow.parquet as pq


def mix_crime() -> pd.DataFrame:
    dfs = []
    for year in range(2015, 2022):
        data = pkgutil.get_data(__name__, f"{year}.parquet")
        if not data:
            raise RuntimeError(f"{year}.csv gave us zero bytes")
        dfs.append(pq.read_table(io.BytesIO(data)).to_pandas())

    ret = pd.concat(dfs)
    return ret
