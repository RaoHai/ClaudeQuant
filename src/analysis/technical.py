"""技术指标计算模块"""

import pandas as pd
import numpy as np

def calculate_ma(data: pd.Series, period: int) -> pd.Series:
    """计算移动平均线"""
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """计算指数移动平均线"""
    return data.ewm(span=period, adjust=False).mean()


def calculate_macd(
    data: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.DataFrame:
    """计算 MACD 指标"""
    fast_ema = calculate_ema(data, fast_period)
    slow_ema = calculate_ema(data, slow_period)

    macd = fast_ema - slow_ema
    signal = calculate_ema(macd, signal_period)
    histogram = macd - signal

    return pd.DataFrame({
        'macd': macd,
        'signal': signal,
        'histogram': histogram
    })


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI 指标"""
    delta = data.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_bollinger_bands(
    data: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> pd.DataFrame:
    """计算布林带"""
    middle = calculate_ma(data, period)
    std = data.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return pd.DataFrame({
        'middle': middle,
        'upper': upper,
        'lower': lower
    })
