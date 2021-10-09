![Build Status](https://github.com/lhayhurst/pdxcrime/actions/workflows/python-app.yml/badge.svg)

# pdxcrime
A data repository for pdx crime and real estate data, with Python code for cleansing and preparing the data to be joined by neighborhood. 

Data sources:
* [2015 PDX real estate (waybackmachine)](https://web.archive.org/web/20161024193831/https://www.pdxmonthly.com/pages/real-estate-2015)
* [2016 PDX real estate](https://www.pdxmonthly.com/news-and-city-life/2016/04/real-estate-2016-the-city)
* [2017 PDX real estate](https://www.pdxmonthly.com/home-and-real-estate/2017/03/portland-neighborhoods-by-the-numbers-2017-the-city)
* [2018 PDX real estate](https://www.pdxmonthly.com/home-and-real-estate/2018/03/portland-neighborhoods-by-the-numbers-2018-the-city)
* [2019 PDX real estate](https://www.pdxmonthly.com/home-and-real-estate/2019/03/portland-neighborhoods-by-the-numbers-2019-the-city)
* [2020 PDX real estate](https://www.pdxmonthly.com/home-and-real-estate/portland-neighborhoods-by-the-numbers-2020-the-city)
* [2021 PDX real estate](https://www.pdxmonthly.com/home-and-real-estate/2021/07/portland-oregon-city-real-estate-data-2021)
* [2015-2021 PDX crime data](https://www.portlandoregon.gov/police/71978)

The raw csv files are checked into this repo and can be found [in the data lake package](src/pdxcrime/data/lake). The "mixed" (cleansed and prepped) files are also checked into this repo and can be found [in the data bar package](src/pdxcrime/data/bar). Tests that analyze data integrity can be found [here](test/test_data_lake.py) and [here](test/test_data_bar.py).

## Getting Started

1. Install python3. The [first article]((https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)) in the series linked above should get you started (he recommends `pyenv`). For example, if using `pyenv`, run "pyenv local 3.9.2" (if using python v 3.9.2).
2. Install `poetry`; see the project homepage or [this article](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/).
3. Build the project. If you prefer make, you can run:

```bash
make deps
```

This will run `poetry install` and `poetry run nox --install-only`. You can run `make help` to see more make targets. Alternatively, you can just run `poetry`'s CLI; see [the Makefile](Makefile)'s make targets for inspiration. 

```bash
make clean
```

Will clean out your install. 

## Configuration

This file has some standard config files:

* The overall project is configured via a [PEP518](https://www.python.org/dev/peps/pep-0518/) [pyproject.toml](pyproject.toml) file. If you fork this repo, you should probably change it. It contains the [black](https://pypi.org/project/black/) settings, the project dependencies, a [pytest](https://docs.pytest.org/en/stable/index.html) configuration, and a 
* the [.gitignore](.gitignore) contains obvious gitignores. 
* the [noxfile.py](noxfile.py) contains nox targets for running `safety` and your `tests`. It uses the [nox-poetry](https://pypi.org/project/nox-poetry/) project for nox-poetry integration.
* The [.flake8](.flake8) has a minimal [flake8](https://flake8.pycqa.org/en/latest/) configuration.
* The [mypy.ini](mypy.ini) has a minimal [mypy](http://mypy-lang.org/) configuration.
