import io

import pytest

from pdxcrime import get_crime
from pdxcrime.data.lake.crime import cleanse_and_prep_crime_data, get_expected_crime_year_csv_header
from pdxcrime.data.lake.neighborhoods import cleanse_and_prep_neighborhoods_data, get_neighborhoods
from pdxcrime.data.lake.real_estate import cleanse_and_prep_real_estate_data, get_real_estate


@pytest.mark.parametrize("bad_year", [2014, 2022])
def test_raise_on_unsupported_crime_year(bad_year):
    with pytest.raises(AssertionError, match="I only have"):
        get_crime(bad_year)


@pytest.mark.parametrize("good_year", list(range(2015, 2022)))
def test_crime_years_have_expected_headers(good_year):
    bio: io.BytesIO = get_crime(good_year)
    assert bio
    header = bio.readline().decode("utf-8")
    assert header.rstrip() == get_expected_crime_year_csv_header(good_year)


@pytest.mark.parametrize("good_year", list(range(2015, 2022)))
def test_cleanse_and_prep_crime(good_year):
    df = cleanse_and_prep_crime_data(good_year, get_crime(good_year))
    assert len(df)


@pytest.mark.parametrize("bad_year", [2014, 2022])
def test_raise_on_unsupported_real_estate_year(bad_year):
    with pytest.raises(AssertionError, match="I only have"):
        get_real_estate(bad_year)


@pytest.mark.parametrize("good_year", list(range(2015, 2022)))
def test_cleanse_and_prep_real_estate_data(good_year):
    bio: io.BytesIO = get_real_estate(good_year)
    assert bio
    df = cleanse_and_prep_real_estate_data(good_year, bio)
    assert len(df)


def test_cleanse_and_prep_neighborhood_data():
    bio: io.BytesIO = get_neighborhoods()
    assert bio
    df = cleanse_and_prep_neighborhoods_data(bio)
    assert len(df) > 0


@pytest.mark.parametrize("year", list(range(2015, 2022)))
def test_can_join_on_neighborhoods(year):
    crimedf = cleanse_and_prep_crime_data(year, get_crime(year))
    redf = cleanse_and_prep_real_estate_data(year, get_real_estate(year))

    c, r = set(crimedf.Neighborhood.values), set(redf.Neighborhood.values)

    assert c - r == set() or c - r == {"NORTHWEST INDUSTRIAL"}, c - r
    assert (
        r - c == set() or r - c == {"DUNTHORPE"} or r - c == {"MULT CO RIVERDALE AREA (DUNTHORPE)"}
    ), (r - c)
