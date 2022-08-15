# Binance token price prediction

This is *demo* project for show how to use [Binance API](https://www.binance.com/en/binance-api),
[Binance Archive](https://data.binance.vision/?prefix=data/spot/daily/klines/) data and Machine Learning
to predict token pricing.



## Scripts
* `binance_import.py` - simple script for import all history of price into database
* `binance_saver.py` - script for real-time price updating
* `hyperparamater_tuning.py` - script for auto-tuning ML model hyperparameter's based on provided historycal data
* `main.py` - main worker for predict token price in real-time mode