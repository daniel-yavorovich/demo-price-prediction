import logging
import time
from datetime import datetime

from binance.spot import Spot
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from settings import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, BINANCE_SAVER_RUN_INTERVAL, \
    BINANCE_PAIR, BINANCE_CHART_INTERVAL, BINANCE_SAVER_ITERATION_LIMIT


def fill_database(symbol=BINANCE_PAIR, interval=BINANCE_CHART_INTERVAL, limit=BINANCE_SAVER_ITERATION_LIMIT):
    for i in client.klines(symbol, interval, limit=limit):
        for time_type in ["open", "close"]:
            if time_type == "open":
                t = datetime.fromtimestamp(int(i[0]) / 1000.0)
            else:
                t = datetime.fromtimestamp(int(i[6]) / 1000.0)

            write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, Point("price")
                            .tag("time_type", time_type)
                            .tag("symbol", BINANCE_PAIR)
                            .tag("source", "Binance")
                            .field("price_open", float(i[1]))
                            .field("price_high", float(i[2]))
                            .field("price_low", float(i[3]))
                            .field("price_close", float(i[4]))
                            .field("price_avg", ((float(i[2]) + float(i[3])) / 2.0))
                            .time(t))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    client = Spot()

    influx = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    logging.info('Worker initialized')

    while True:
        fill_database()
        logging.info('Iteration completed. Sleep {} sec'.format(BINANCE_SAVER_RUN_INTERVAL))
        time.sleep(BINANCE_SAVER_RUN_INTERVAL)
