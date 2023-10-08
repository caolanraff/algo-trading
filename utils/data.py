import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf

yf.pdr_override()


def load_financial_data(ticker, start_date, end_date, output_file):
    data_dir = '/Users/caolanraff/Development/projects/algo-trading/data/'
    try:
        df = pd.read_pickle(data_dir + output_file)
        print(output_file + ' data file found...reading from file')
    except FileNotFoundError:
        print('File not found...downloading data')
        df = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
        df = df[start_date:end_date]
        df.to_pickle(data_dir + output_file)
    return df