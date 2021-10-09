import io
import pkgutil

import pandas as pd


def get_neighborhoods() -> io.BytesIO:
    data = pkgutil.get_data(__name__, f"Neighborhoods.csv")
    if not data:
        raise RuntimeError(f"Neighborhoods.csv gave us zero bytes")
    return io.BytesIO(data)


def cleanse_and_prep_neighborhoods_data(bytes_io: io.BytesIO) -> pd.DataFrame:
    df = pd.read_csv(bytes_io)
    df = df.rename(columns={"NAME": "Neighborhood"})
    return df
