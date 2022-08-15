# Binance token price prediction

This is *demo* project for show how to use [Binance API](https://www.binance.com/en/binance-api),
[Binance Archive](https://data.binance.vision/?prefix=data/spot/daily/klines/) data and Machine Learning
to predict token pricing.

This demo use [Facebook Prophet](https://facebook.github.io/prophet/) for forecasting
and [InfluxDB](https://www.influxdata.com/products/influxdb/) as main database. 

## Requirements

You need to install InfluxDB and create bucket, after that please fill `INFLUXDB_*` settings parameters in `settings.py`

## Scripts
* `binance_import.py` - simple script for import all history of price into database
* `binance_saver.py` - script for real-time price updating
* `hyperparamater_tuning.py` - script for auto-tuning ML model hyperparameter's based on provided historycal data
* `main.py` - main worker for predict token price in real-time mode