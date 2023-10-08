import numpy as np
from sklearn.model_selection import train_test_split


def create_classification_trading_condition(df):
    '''
    The classification response variable is +1 if the close price tomorrow is higher
    than the close price today, and -1 if the close price tomorrow is lower than
    the close price today.
    '''
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, -1)
    df = df.dropna()
    X = df[['Open-Close', 'High-Low']]
    Y = df[['Target']]
    return (df, X, Y)


def create_regression_trading_condition(df):
    '''
    The regression response variable is positive if the price goes up tomorrow,
    negative if the price goes down tomorrow and zero if there is no change.
    The magnitude of the response variable captures the magnitude of the price move.
    '''
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df['Target'] = df['Close'].shift(-1) - df['Close']
    df = df.dropna()
    X = df[['Open-Close', 'High-Low']]
    Y = df[['Target']]
    return (df, X, Y)


def create_train_split_group(X, Y, split_ratio=0.8):
    return train_test_split(X, Y, shuffle=False, train_size=split_ratio)