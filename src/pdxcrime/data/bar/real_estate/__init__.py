import io
from typing import List

import pandas as pd
import pyarrow.parquet as pq

import pkgutil


def mix_real_estate(years: List[int]) -> pd.DataFrame:
    expected_years = list(range(2015, 2022))
    dfs = []
    for year in years:
        if year not in expected_years:
            raise RuntimeError(f"{year} is not in {expected_years}")

        data = pkgutil.get_data(__name__, f"{year}.parquet")
        if not data:
            raise RuntimeError(f"{year}.parquet gave us zero bytes")

        dfs.append(pq.read_table(io.BytesIO(data)).to_pandas())

    df = pd.concat(dfs)
    return df
