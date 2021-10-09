"""Command-line interface."""
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import typer

from pdxcrime.data.lake.crime import cleanse_and_prep_crime_data, get_crime
from pdxcrime import __version__ as pdxcrime_version
from pdxcrime.data.lake.real_estate import cleanse_and_prep_real_estate_data, get_real_estate

app = typer.Typer()


@app.command()
def mix_parquet_files(target: str, output_path: str):
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


@app.command()
def version():
    typer.echo(pdxcrime_version)


if __name__ == "__main__":
    app()
