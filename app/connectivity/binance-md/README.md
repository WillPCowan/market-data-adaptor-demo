# Binance Market Data Adaptor
## Install Dependencies
```
poetry install
```
## Run
```
poetry run python src/connectivity/binance_md/__main__.py
```
Example config
```
http_uri: https://api.binance.com/api/v3
ws_uri: wss://stream.binance.com:9443/ws
symbol: BTCUSDT
depth: 100
```

## Test
```
poetry run pytest
```