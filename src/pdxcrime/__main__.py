"""Command-line interface."""
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from pdxcrime import __version__ as pdxcrime_version
from pdxcrime.data.lake.crime import cleanse_and_prep_crime_data, get_crime
from pdxcrime.data.lake.real_estate import cleanse_and_prep_real_estate_data, get_real_estate

app = typer.Typer()


@app.command()
def mix_parquet_files(target: str, output_path: str) -> None:
    op = Path(output_path)
    if not op.parent.exists():
        raise RuntimeError(f"{op.parent} does not exist, no place to save")
    for year in range(2015, 2022):
        if target == "crime":
            # see the test test_can_roundtrip_csv_to_pandas_to_arrow_to_parquet_to_arrow_to_pandas
            crime_df = cleanse_and_prep_crime_data(year, get_crime(year))
            parquet_file = op / f"{year}.parquet"
            typer.echo(f"writing {parquet_file}")
            pq.write_table(pa.Table.from_pandas(crime_df), str(parquet_file))
        elif target == "real-estate":
            re_df = cleanse_and_prep_real_estate_data(year, get_real_estate(year))
            parquet_file = op / f"{year}.parquet"
            typer.echo(f"writing {parquet_file}")
            pq.write_table(pa.Table.from_pandas(re_df), str(parquet_file))
    return


@app.command()
def mix_csv_files(output_path: str) -> None:
    op = Path(output_path)
    if not op.parent.exists():
        raise RuntimeError(f"{op.parent} does not exist, no place to save")

    crime_dfs = []
    real_estate_dfs = []

    typer.echo("Cleaning data for 2015-2022")
    for year in range(2015, 2022):
        crime_df = cleanse_and_prep_crime_data(year, get_crime(year))
        crime_dfs.append(crime_df)
        re_df = cleanse_and_prep_real_estate_data(year, get_real_estate(year))
        real_estate_dfs.append(re_df)

    crime_df: pd.DataFrame = pd.concat(crime_dfs)

    crime_csv = op / "pdx_crime_2015_2022.csv"
    typer.echo(f"Cutting {crime_csv}")
    crime_df.to_csv(str(crime_csv), index=False)

    real_estate_df = pd.concat(real_estate_dfs)
    real_estate_csv = op / "pdx_real_estate_2015_2022.csv"
    typer.echo(f"Cutting {real_estate_csv}")
    real_estate_df.to_csv(str(real_estate_csv), index=False)

    return


@app.command()
def version() -> None:
    typer.echo(pdxcrime_version)
    return


if __name__ == "__main__":
    app()
