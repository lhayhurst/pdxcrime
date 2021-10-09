import io
import pkgutil

import numpy as np
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
        if "$" in x:
            x = x.replace("$", "")
        if "," in x:
            x = x.replace(",", "")
        if "%" in x:
            x = x.replace("%", "")
    return x


def cleanse_and_prep_real_estate_data(year: int, bytes_io: io.BytesIO) -> pd.DataFrame:
    df = pd.read_csv(bytes_io, na_values=["Ñ"])
    assert set(df.Year.unique()) == {year}, f"Unexpected year in data: {df.Year.unique()}"
    df.Year = df.Year.astype(int)

    # start cleaning up the rest of the columns
    df = _cleanup_quant_columns(df, year)

    # clean up the neighborhood column
    df = _cleanup_neighborhoods(df, year)

    return df


def _cleanup_quant_columns(df, year):
    if year == 2021:
        avg_sale_price = df.columns[3]
    else:
        avg_sale_price = df.columns[2]

    assert "Average Price" in avg_sale_price or "Average home sale price ($)", avg_sale_price
    df = df.rename(columns={avg_sale_price: "AverageSalePrice"})
    df.AverageSalePrice = df.AverageSalePrice.replace({"—": "NaN"})
    df.AverageSalePrice = df.AverageSalePrice.apply(clean_currency)
    df.AverageSalePrice = df.AverageSalePrice.astype("float")

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
    df.MedianSalePrice = df.MedianSalePrice.replace({"—": "NaN", "–": "NaN"})
    df.MedianSalePrice = df.MedianSalePrice.apply(clean_currency)
    df.MedianSalePrice = df.MedianSalePrice.astype("float")

    avg_cost_per_sq_foot = df.columns[4]
    assert (
        "Cost per Sq. Ft. (avg)" in avg_cost_per_sq_foot
        or "Average cost per square foot ($)" in avg_cost_per_sq_foot
    ), avg_cost_per_sq_foot
    df = df.rename(columns={avg_cost_per_sq_foot: "AverageCostPerSqFoot"})
    df.AverageCostPerSqFoot = df.AverageCostPerSqFoot.replace({"—": "NaN", "–": "NaN"})
    df.AverageCostPerSqFoot = df.AverageCostPerSqFoot.apply(clean_currency)
    df.AverageCostPerSqFoot = df.AverageCostPerSqFoot.astype("float")

    # the rest of the the cleanup
    days_on_market_index = 5
    homes_sold_index = 6
    condo_sales_index = 7

    if year == 2021:
        distressed_property_sales_index = 14
        year_build_index = 11
        one_year_median_price_index = 9
        five_year_median_price_index = 10

    else:
        one_year_median_price_index = 8
        five_year_median_price_index = 9
        distressed_property_sales_index = 10
        year_build_index = 11

    todos = [
        (days_on_market_index, "Days on market", "AverageDaysOnMarket"),
        (homes_sold_index, "Homes sold", "CountHomesSold"),
        (condo_sales_index, "Condo sales", "CondoSalesPercentage"),
        (
            one_year_median_price_index,
            "1-year Median Price Change",
            "MedianOneYearPriceChangePercentage",
        ),
        (
            five_year_median_price_index,
            "5-year Median Price Change",
            "MedianFiveYearPriceChangePercentage",
        ),
        (
            distressed_property_sales_index,
            "Distressed",
            "DistressedPropertySalesPercentage",
        ),
        (year_build_index, "Year built", "AverageYearBuilt"),
    ]

    for idx, old_name, new_name in todos:
        c: str = df.columns[idx]
        assert old_name.lower() in c.lower(), f"{old_name} not in {c}"
        df = df.rename(columns={c: new_name})
        df[new_name] = df[new_name].replace({"—": "NaN", "–": "NaN"})
        df[new_name] = df[new_name].apply(clean_currency)
        df[new_name] = df[new_name].astype("float")
    return df


def _cleanup_neighborhoods(df, year):
    neigh = df.columns[1]
    assert "Neighborhood" in neigh
    df = df.rename(columns={neigh: "Neighborhood"})
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
        woodstock_2018 = cleanse_and_prep_real_estate_data(2018, get_real_estate(2018))
        woodstock_2018 = woodstock_2018[woodstock_2018.Neighborhood == "WOODSTOCK"]
        sampled_columns = [
            "AverageSalePrice",
            "MedianSalePrice",
            "AverageDaysOnMarket",
            "CountHomesSold",
            "CondoSalesPercentage",
            "MedianOneYearPriceChangePercentage",
            "DistressedPropertySalesPercentage",
            "AverageYearBuilt",
        ]
        woodstock_2018 = woodstock_2018[sampled_columns]

        woodstock_2020 = cleanse_and_prep_real_estate_data(2020, get_real_estate(2020))
        woodstock_2020 = woodstock_2020[woodstock_2020.Neighborhood == "WOODSTOCK"]
        woodstock_2020 = woodstock_2020[sampled_columns]

        woodstock_2019 = (woodstock_2018 + woodstock_2020) / 2
        new_row = [2019, "WOODSTOCK"] + list(woodstock_2019.iloc[0].values)
        lnr = len(new_row)
        new_row = new_row + list(np.repeat(np.nan, len(df.columns) - lnr))
        df.loc[len(df.index) + 1] = new_row
        print(len(df))
    return df
