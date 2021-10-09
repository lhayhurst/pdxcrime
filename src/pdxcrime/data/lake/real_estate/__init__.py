import io
import pkgutil

import pandas as pd


def get_real_estate(year: int) -> io.BytesIO:
    assert year in range(2015, 2022), "I only have 2015->2021 data"
    data = pkgutil.get_data(__name__, f"{year}.csv")
    if not data:
        raise RuntimeError(f"{year}.csv gave us zero bytes")
    return io.BytesIO(data)


def clean_currency(x):
    """If the value is a string, then remove currency symbol and delimiters
    otherwise, the value is numeric and can be converted
    """
    if isinstance(x, str):
        if "$" in x or "," in x:
            return x.replace("$", "").replace(",", "")
        else:
            return 0
    return x


def cleanse_and_prep_real_estate_data(year: int, bytes_io: io.BytesIO) -> pd.DataFrame:
    df = pd.read_csv(bytes_io)
    assert set(df.Year.unique()) == {year}, f"Unexpected year in data: {df.Year.unique()}"

    # clean up the neighborhood column
    neigh = df.columns[1]
    assert "Neighborhood" in neigh
    df = df.rename(columns={neigh: "Neighborhood"})

    if year == 2021:
        avg_sale_price = df.columns[3]
    else:
        avg_sale_price = df.columns[2]

    assert "Average Price" in avg_sale_price or "Average home sale price ($)", avg_sale_price
    df = df.rename(columns={avg_sale_price: "AverageSalePrice"})
    df.AverageSalePrice = df.AverageSalePrice.apply(clean_currency).astype("float")

    if year == 2021:
        median_sale_price = df.columns[2]
    else:
        median_sale_price = df.columns[3]

    assert (
        "Median Price" in median_sale_price
        or "Median home sale price ($)" in median_sale_price
        or "Median 2020 home sale price ($)" in median_sale_price
    ), median_sale_price
    df = df.rename(columns={median_sale_price: "MedianSalePrice"})
    df.MedianSalePrice = df.MedianSalePrice.apply(clean_currency).astype("float")

    avg_cost_per_sq_foot = df.columns[4]
    assert (
        "Cost per Sq. Ft. (avg)" in avg_cost_per_sq_foot
        or "Average cost per square foot ($)" in avg_cost_per_sq_foot
    ), avg_cost_per_sq_foot
    df = df.rename(columns={avg_cost_per_sq_foot: "AverageCostPerSqFoot"})

    df.Neighborhood = df.Neighborhood.str.upper()

    df = df[~(df.Neighborhood == "TOTAL")]  # this one shows up in the 2017 data, line 90
    df = df[~(df.Neighborhood == "PORTLAND TOTAL**")]  # this one shows up in 2018 data
    df = df[~(df.Neighborhood == "PORTLAND TOTAL")]  # this one shows up in 2021 data

    transl = {
        "MT SCOTT-ARLETA": "MT. SCOTT-ARLETA",
        "MT SCOTT ARLETA": "MT. SCOTT-ARLETA",
        "SULLIVAN’S GULCH": "SULLIVAN'S GULCH",
        "SULLIVANS GULCH": "SULLIVAN'S GULCH",
        "MT TABOR": "MT. TABOR",
        "ARDENWALD-JOHNSON CREEK": "ARDENWALD/JOHNSON CREEK",
        "BRENTWOOD/ DARLINGTON": "BRENTWOOD/DARLINGTON",
        "BRENTWOOD-DARLINGTON": "BRENTWOOD/DARLINGTON",
        "OLD TOWN/ CHINATOWN": "OLD TOWN/CHINATOWN",
        "OLD TOWN CHINATOWN": "OLD TOWN/CHINATOWN",
        "PEARL": "PEARL DISTRICT",
        "ARDENWALD-JOHNSON CREEK*": "ARDENWALD/JOHNSON CREEK",
        "PLEASANT VALLEY*": "PLEASANT VALLEY",
        "BRIDLEMILE*": "BRIDLEMILE",
        "FOREST PARK*": "FOREST PARK",
        "LINNTON*": "LINNTON",
        "SOUTHWEST HILLS*": "SOUTHWEST HILLS",
        "SYLVAN-HIGHLANDS*": "SYLVAN-HIGHLANDS",
        "SYLVAN HIGHLANDS*": "SYLVAN-HIGHLANDS",
        "POWELLHURST GILBERT": "POWELLHURST-GILBERT",
        "SELLWOOD MORELAND IMPROVEMENT LEAGUE": "SELLWOOD-MORELAND",
    }
    df.Neighborhood = df.Neighborhood.replace(transl)

    if year == 2019:
        # Woodstock is missing for this year
        # set it to halfway between the 2018 and 2020 value
        woodstock_2018 = cleanse_and_prep_real_estate_data(2018, get_real_estate(2018))[
            ["Year", "AverageSalePrice", "MedianSalePrice"]
        ]
        woodstock_2020 = cleanse_and_prep_real_estate_data(2020, get_real_estate(2020))[
            ["Year", "AverageSalePrice", "MedianSalePrice"]
        ]

        woodstock_2019 = (woodstock_2018 + woodstock_2020) / 2
        woodstock_2019["Neighborhood"] = "WOODSTOCK"
        df = df.append(woodstock_2019, ignore_index=True)

    return df
