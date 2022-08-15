import itertools
from multiprocessing import freeze_support

import pandas as pd
from influxdb_client import InfluxDBClient
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from main import get_history_data
from settings import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG

param_grid = {
    'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
    'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
}

# Generate all combinations of parameters
all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
rmses = []  # Store the RMSEs for each params here

# Use cross validation to evaluate all parameters


if __name__ == '__main__':
    freeze_support()

    influx = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = influx.query_api()
    data = get_history_data(query_api)

    df = pd.DataFrame.from_dict(data)
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])

    for params in all_params:
        m = Prophet(**params).fit(df)  # Fit model with given params
        df_cv = cross_validation(m, horizon='5 minutes', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=1)
        rmses.append(df_p['rmse'].values[0])

    # Find the best parameters
    tuning_results = pd.DataFrame(all_params)
    tuning_results['rmse'] = rmses
    print(tuning_results)
