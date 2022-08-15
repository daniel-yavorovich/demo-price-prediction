#!/usr/bin/env python
"""
This script will import all history of pricing from
Binance archive: https://data.binance.vision/?prefix=data/spot/daily/klines/
"""
import csv
import logging
import os
import time
from datetime import datetime, timedelta
import zipfile
import tempfile
from io import BytesIO

import requests
from binance.spot import Spot
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from settings import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, BINANCE_SAVER_RUN_INTERVAL, \
    BINANCE_PAIR, BINANCE_CHART_INTERVAL


def run_import(symbol=BINANCE_PAIR, interval=BINANCE_CHART_INTERVAL):
    date = datetime.now()
    while True:
        date = date - timedelta(days=1)
        url = 'https://data.binance.vision/data/spot/daily/klines/' \
              '{symbol}/{interval}/{symbol}-{interval}-{date}.zip'.format(symbol=symbol,
                                                                          interval=interval,
                                                                          date=date.strftime('%Y-%m-%d'))

        req = requests.get(url)
        z = zipfile.ZipFile(BytesIO(req.content))

        fname = '{symbol}-{interval}-{date}.csv'.format(symbol=symbol,
                                                        interval=interval,
                                                        date=date.strftime('%Y-%m-%d'))
        tmp_dir = tempfile.TemporaryDirectory()
        z.extract(fname, tmp_dir.name)

        with open(os.path.join(tmp_dir.name, fname)) as f:
            csvreader = csv.reader(f, delimiter=',', quotechar='|')
            for i in csvreader:
                for time_type in ["open", "close"]:
                    write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, Point("price")
                                    .tag("time_type", time_type)
                                    .tag("symbol", BINANCE_PAIR)
                                    .tag("source", "Binance")
                                    .field("price_open", float(i[1]))
                                    .field("price_high", float(i[2]))
                                    .field("price_low", float(i[3]))
                                    .field("price_close", float(i[4]))
                                    .field("price_avg", ((float(i[2]) + float(i[3])) / 2.0))
                                    .time(datetime.fromtimestamp(int(i[0]) / 1000.0)))

        logging.info('File {} imported'.format(fname))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    client = Spot()

    influx = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    logging.info('Worker initialized')

    while True:
        run_import()
        logging.info('Iteration completed. Sleep {} sec'.format(BINANCE_SAVER_RUN_INTERVAL))
        time.sleep(BINANCE_SAVER_RUN_INTERVAL)
