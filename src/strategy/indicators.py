"""技术指标计算模块"""

import pandas as pd
import numpy as np
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_ma(data: pd.Series, period: int) -> pd.Series:
    """
    计算移动平均线

    Args:
        data: 价格数据（通常是收盘价）
        period: 周期

    Returns:
        移动平均线 Series
    """
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    计算指数移动平均线

    Args:
        data: 价格数据
        period: 周期

    Returns:
        EMA Series
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_macd(
    data: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.DataFrame:
    """
    计算 MACD 指标

    Args:
        data: 价格数据（通常是收盘价）
        fast_period: 快线周期
        slow_period: 慢线周期
        signal_period: 信号线周期

    Returns:
        DataFrame with columns: ['macd', 'signal', 'histogram']
    """
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
    """
    计算 RSI 指标

    Args:
        data: 价格数据
        period: 周期

    Returns:
        RSI Series (0-100)
    """
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
    """
    计算布林带

    Args:
        data: 价格数据
        period: 周期
        std_dev: 标准差倍数

    Returns:
        DataFrame with columns: ['middle', 'upper', 'lower']
    """
    middle = calculate_ma(data, period)
    std = data.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return pd.DataFrame({
        'middle': middle,
        'upper': upper,
        'lower': lower
    })


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    计算平均真实波幅 (ATR)

    Args:
        high: 最高价
        low: 最低价
        close: 收盘价
        period: 周期

    Returns:
        ATR Series
    """
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()

    return atr


def calculate_volume_ma(volume: pd.Series, period: int) -> pd.Series:
    """
    计算成交量移动平均

    Args:
        volume: 成交量
        period: 周期

    Returns:
        Volume MA Series
    """
    return volume.rolling(window=period).mean()


def calculate_crossover(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """
    计算金叉死叉信号

    Args:
        fast: 快线
        slow: 慢线

    Returns:
        Series: 1 表示金叉（fast上穿slow），-1 表示死叉（fast下穿slow），0 表示无信号
    """
    prev_fast = fast.shift(1)
    prev_slow = slow.shift(1)

    # 金叉: 快线上穿慢线
    golden_cross = (fast > slow) & (prev_fast <= prev_slow)

    # 死叉: 快线下穿慢线
    death_cross = (fast < slow) & (prev_fast >= prev_slow)

    signals = pd.Series(0, index=fast.index)
    signals[golden_cross] = 1
    signals[death_cross] = -1

    return signals


def add_indicators_to_data(df: pd.DataFrame, indicators: dict) -> pd.DataFrame:
    """
    批量添加指标到 DataFrame

    Args:
        df: 原始数据（必须包含 OHLCV 列）
        indicators: 指标配置字典

    Returns:
        添加了指标列的 DataFrame

    Example:
        indicators = {
            'ma5': {'type': 'ma', 'period': 5},
            'ma20': {'type': 'ma', 'period': 20},
            'rsi': {'type': 'rsi', 'period': 14}
        }
    """
    result = df.copy()

    for name, config in indicators.items():
        indicator_type = config.get('type')

        if indicator_type == 'ma':
            period = config.get('period', 20)
            result[name] = calculate_ma(df['close'], period)

        elif indicator_type == 'ema':
            period = config.get('period', 20)
            result[name] = calculate_ema(df['close'], period)

        elif indicator_type == 'rsi':
            period = config.get('period', 14)
            result[name] = calculate_rsi(df['close'], period)

        elif indicator_type == 'macd':
            macd_df = calculate_macd(df['close'])
            result[f'{name}_macd'] = macd_df['macd']
            result[f'{name}_signal'] = macd_df['signal']
            result[f'{name}_histogram'] = macd_df['histogram']

        elif indicator_type == 'bollinger':
            period = config.get('period', 20)
            std_dev = config.get('std_dev', 2.0)
            bb_df = calculate_bollinger_bands(df['close'], period, std_dev)
            result[f'{name}_middle'] = bb_df['middle']
            result[f'{name}_upper'] = bb_df['upper']
            result[f'{name}_lower'] = bb_df['lower']

        else:
            logger.warning(f"Unknown indicator type: {indicator_type}")

    return result
