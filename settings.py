import os


def check_env(key):
    if not os.environ.get(key):
        raise BaseException('OS env {} not provided'.format(key))


INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET')
BINANCE_SAVER_RUN_INTERVAL = int(os.environ.get('BINANCE_SAVER_RUN_INTERVAL', 10))  # 1 min
BINANCE_SAVER_ITERATION_LIMIT = int(os.environ.get('BINANCE_SAVER_ITERATION_LIMIT', 30))  # 10 min

BINANCE_PAIR = os.environ.get('BINANCE_PAIR', 'OGNBTC')
BINANCE_CHART_INTERVAL = os.environ.get('BINANCE_CHART_INTERVAL', '1m')

FORECAST_HORIZON = int(os.environ.get('FORECAST_HORIZON', '60'))

check_env('INFLUXDB_TOKEN')
check_env('INFLUXDB_ORG')
check_env('INFLUXDB_BUCKET')
