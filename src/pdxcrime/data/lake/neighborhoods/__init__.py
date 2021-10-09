import io
import pkgutil

import pandas as pd


def get_neighborhoods() -> io.BytesIO:
    return io.BytesIO(pkgutil.get_data(__name__, "Neighborhoods.csv"))


def cleanse_and_prep_neighborhoods_data(bytes_io: io.BytesIO) -> pd.DataFrame:
    df = pd.read_csv(bytes_io)
    df = df.rename(columns={"NAME": "Neighborhood"})
    return df
