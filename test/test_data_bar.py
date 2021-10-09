from pdxcrime.data.bar.crime import mix_crime
from pdxcrime.data.bar.real_estate import mix_real_estate


def test_can_mix_real_estate_from_data_bar():
    df = mix_real_estate()
    assert len(df)
    assert set(df.Year.unique()) == set(range(2015, 2022))

    for gt_zero_col in [
        "AverageSalePrice",
        "MedianSalePrice",
        "AverageCostPerSqFoot",
        "AverageDaysOnMarket",
        "AverageYearBuilt",
    ]:
        assert len(df[df[gt_zero_col] <= 0]) == 0


def test_can_mix_crime_from_data_bar():
    df = mix_crime()
    assert len(df)
    assert set(df.Year.unique()) == set(range(2015, 2022))
