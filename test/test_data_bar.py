from pdxcrime.data.bar.real_estate import mix_real_estate


def test_can_mix_real_estate_from_data_bar():
    df = mix_real_estate(range(2015, 2022))
    assert len(df)
