from prefect import Flow, task
from ocandata.statscan import StatscanZip
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

@task
def download_prices():
    return StatscanZip('https://www150.statcan.gc.ca/n1/tbl/csv/18100251-eng.zip').get_data()


@task
def save_prices(prices):
    prices_filename = '../data/prices.parquet'
    prices.to_parquet(prices_filename)
    return prices_filename


@task
def chart_retail_prices(prices_file):
    '''Print the result'''
    prices = pd.read_parquet(prices_file)
    print("Received y: {}".format(len(prices)))
    return prices_file


with Flow("ETL") as flow:
    e = download_prices()
    t = save_prices(e)
    l = chart_retail_prices(t)


flow.run()