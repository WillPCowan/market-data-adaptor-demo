# Market Data Adaptors
## Getting started
1. Install poetry `curl -sSL https://install.python-poetry.org | python3 -` (https://python-poetry.org/docs/)
2. (optional) `poetry config virtualenvs.in-project true`
3. Install dependencies of libs/apps you want to use, e.g.
    ```
    cd lib/connectivity/common
    poetry install
    cd ../../../app/connectivity/binance-md
    poetry install
    ```
4. Run market data connector
    ```
    cd app/connectivity/binance-md
    poetry run python src/demo/connectivity/binance_md/__main__.py
    ```
5. Running tests
    ```
    cd app/connectivity/binance-md
    poetry run pytest
    ```
