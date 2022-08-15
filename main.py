import time

import pandas as pd
from influxdb_client.client.write_api import SYNCHRONOUS
from prophet import Prophet
from influxdb_client import InfluxDBClient, Point
from settings import INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_URL, INFLUXDB_BUCKET, BINANCE_PAIR, FORECAST_HORIZON


def get_history_data(query_api, symbol="OGNBTC", time_type="close", field="price_avg", source="Binance"):
    results = []

    query = 'from(bucket:"{bucket}") ' \
            '|> range(start:-48h) ' \
            '|> filter(fn: (r) => r["_measurement"] == "price") ' \
            '|> filter(fn: (r) => r["symbol"] == "{symbol}") ' \
            '|> filter(fn: (r) => r["source"] == "{source}") ' \
            '|> filter(fn: (r) => r["time_type"] == "{time_type}")' \
            '|> filter(fn: (r) => r["_field"] == "{field}")' \
            '|> yield(name: "mean")'.format(bucket=INFLUXDB_BUCKET, symbol=symbol, source=source, time_type=time_type,
                                            field=field)

    for table in query_api.query(org=INFLUXDB_ORG, query=query):
        for record in table.records:
            results.append([record.get_time().astimezone().replace(tzinfo=None), record.get_value()])

    return results


def forecast(m, symbol="OGNBTC", time_type="close", field="price_avg", FORECAST_HORIZON=10, freq='min'):
    # Load historical data by API
    data = get_history_data(query_api, symbol, time_type, field)

    df = pd.DataFrame.from_dict(data)
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])

    # Fit data
    m.fit(df)

    # Create dates to predict
    future_frame = m.make_future_dataframe(periods=FORECAST_HORIZON, freq=freq, include_history=False)

    # Make predict
    forecasts = m.predict(future_frame)

    return forecasts


def run():
    # Init Prophet
    # params = {'changepoint_prior_scale': 0.001, 'seasonality_prior_scale': 0.01}
    params = {'changepoint_prior_scale': 1, 'seasonality_prior_scale': 0.0001}

    record = {
        'symbol': BINANCE_PAIR
    }
    for time_type in ['open', 'close']:
        for field in ['price_open', 'price_high', 'price_low', 'price_close', 'price_avg']:
            m = Prophet(**params)
            m.stan_backend.logger = None

            forecasts = forecast(m, time_type=time_type, field=field, FORECAST_HORIZON=FORECAST_HORIZON)
            record['time'] = forecasts.ds[FORECAST_HORIZON - 1]
            record['time_type'] = time_type

            # set price field
            value = forecasts.yhat[FORECAST_HORIZON - 1]
            record[field] = value

    write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, Point("price")
                    .tag("time_type", time_type)
                    .tag("symbol", BINANCE_PAIR)
                    .tag("source", "AI")
                    .field("price_open", record['price_open'])
                    .field("price_high", record['price_high'])
                    .field("price_low", record['price_low'])
                    .field("price_close", record['price_close'])
                    .field("price_avg", record['price_avg'])
                    .time(record['time']))
    print(record)
    # m.plot(forecasts, include_legend=True)
    # plt.show()


if __name__ == '__main__':
    # Init influxdb
    influx = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = influx.query_api()
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    while True:
        run()
        time.sleep(60)
