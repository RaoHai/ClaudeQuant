"""实时行情获取模块"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import tushare as ts

from src.core.exceptions import DataProviderError
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class QuoteProvider:
    """实时行情提供者"""

    def __init__(self):
        """初始化"""
        token = os.getenv('TUSHARE_TOKEN')
        if not token:
            raise DataProviderError("TUSHARE_TOKEN not set in environment")

        ts.set_token(token)
        self.pro = ts.pro_api()
        self.config = get_config()

        logger.info("QuoteProvider initialized")

    def get_realtime_quote(self, symbol: str) -> Dict:
        """
        获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            行情字典
        """
        symbol = self._normalize_symbol(symbol)

        try:
            # 获取最新日线数据（作为实时行情）
            today = datetime.now().strftime('%Y%m%d')
            df = self.pro.daily(ts_code=symbol, trade_date=today)

            if df.empty:
                # 如果今天没有数据，获取最近一个交易日
                df = self.pro.daily(ts_code=symbol, start_date=(datetime.now() - timedelta(days=7)).strftime('%Y%m%d'))
                if df.empty:
                    raise DataProviderError(f"No quote data for {symbol}")
                df = df.iloc[0:1]  # 取最新一条

            row = df.iloc[0]

            quote = {
                'symbol': symbol,
                'name': self._get_stock_name(symbol),
                'date': row['trade_date'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'pre_close': row['pre_close'],
                'change': row['change'],
                'pct_change': row['pct_chg'],
                'volume': row['vol'] * 100,  # 手 -> 股
                'amount': row['amount'] * 1000,  # 千元 -> 元
                'turnover_rate': row.get('turnover_rate', 0),
            }

            logger.info(f"Got quote for {symbol}: {quote['close']}")
            return quote

        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            raise DataProviderError(f"Failed to get quote: {e}")

    def get_historical_data(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """
        获取历史数据

        Args:
            symbol: 股票代码
            days: 天数

        Returns:
            DataFrame
        """
        symbol = self._normalize_symbol(symbol)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')  # 多获取一些以确保有足够交易日

        try:
            df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)

            if df.empty:
                raise DataProviderError(f"No historical data for {symbol}")

            # 标准化列名
            df = df.rename(columns={
                'ts_code': 'symbol',
                'trade_date': 'date',
                'pct_chg': 'pct_change',
                'vol': 'volume',
            })

            # 转换日期
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

            # 转换成交量和金额
            df['volume'] = df['volume'] * 100
            df['amount'] = df['amount'] * 1000

            # 按日期升序排序
            df = df.sort_values('date').reset_index(drop=True)

            # 只取最近的指定天数
            df = df.tail(days)

            logger.info(f"Got {len(df)} bars for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            raise DataProviderError(f"Failed to get historical data: {e}")

    def get_portfolio_quotes(self, symbols: List[str]) -> List[Dict]:
        """
        批量获取持仓行情

        Args:
            symbols: 股票代码列表

        Returns:
            行情列表
        """
        quotes = []
        for symbol in symbols:
            try:
                quote = self.get_realtime_quote(symbol)
                quotes.append(quote)
            except Exception as e:
                logger.warning(f"Failed to get quote for {symbol}: {e}")
                continue

        return quotes

    def _get_stock_name(self, symbol: str) -> str:
        """获取股票名称"""
        try:
            df = self.pro.stock_basic(ts_code=symbol, fields='ts_code,name')
            if not df.empty:
                return df.iloc[0]['name']
        except Exception as e:
            logger.warning(f"Failed to get stock name for {symbol}: {e}")

        return symbol

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        if '.' in symbol:
            return symbol.upper()

        # 根据代码前缀判断市场
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith(('0', '3')):
            return f"{symbol}.SZ"
        elif symbol.startswith(('4', '8')):
            return f"{symbol}.BJ"
        else:
            raise ValueError(f"Cannot determine market for symbol: {symbol}")
