import io
import pkgutil

import pandas as pd


def get_crime(year: int) -> io.BytesIO:
    assert year in range(2015, 2022), "I only have 2015->2021 data"
    data = pkgutil.get_data(__name__, f"{year}.csv")
    if not data:
        raise RuntimeError(f"{year}.csv gave us zero bytes")
    return io.BytesIO(data)


CRIME_COLUMNS_TO_USE = (
    "Address,CaseNumber,CrimeAgainst,Neighborhood,OccurDate,OccurTime,OffenseCategory,"
    + "OffenseType,OpenDataLat,OpenDataLon,ReportDate,OffenseCount"
)


def get_expected_crime_year_csv_header(year: int) -> str:
    if year < 2020:
        return (
            "Address,CaseNumber,CrimeAgainst,Neighborhood,OccurDate,OccurTime,OffenseCategory,"
            + "OffenseType,OpenDataLat,OpenDataLon,OpenDataX,OpenDataY,ReportDate,OffenseCount"
        )

    else:
        return CRIME_COLUMNS_TO_USE


def cleanse_and_prep_crime_data(year: int, bytes_io: io.BytesIO) -> pd.DataFrame:
    df = pd.read_csv(bytes_io, parse_dates=["OccurDate", "ReportDate"])
    df = df[CRIME_COLUMNS_TO_USE.split(",")]
    df["Year"] = df.ReportDate.dt.year
    assert set(df.Year.unique()) == {year}, f"Unexpected year in data: {df.Year.unique()}"

    df.Neighborhood = df.Neighborhood.str.upper()

    # clean up the crime data to match the real-estate data
    transl = {
        "ST JOHNS": "ST. JOHNS",
        "LLOYD": "LLOYD DISTRICT",
        "MT TABOR": "MT. TABOR",
        "NORTHWEST": "NORTHWEST DISTRICT",
        "ARDENWALD": "ARDENWALD/JOHNSON CREEK",
        "MT SCOTT-ARLETA": "MT. SCOTT-ARLETA",
        "PEARL": "PEARL DISTRICT",
        "BRENTWOOD-DARLINGTON": "BRENTWOOD/DARLINGTON",
        "BUCKMAN WEST": "BUCKMAN",
        "BUCKMAN EAST": "BUCKMAN",
    }
    df.Neighborhood = df.Neighborhood.replace(transl)

    # drop records where the neighborhood is nan
    df = df[~(df.Neighborhood.isna())]
    return df
