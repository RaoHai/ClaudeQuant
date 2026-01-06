"""实时行情获取模块 - 基于 AkShare"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import akshare as ak

from src.core.exceptions import DataProviderError
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class QuoteProvider:
    """实时行情提供者 - 使用 AkShare 数据源"""

    def __init__(self):
        """初始化"""
        self.config = get_config()
        logger.info("QuoteProvider initialized with AkShare")

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
            # 使用 AkShare 获取实时行情
            # stock_zh_a_spot_em 返回全市场数据，我们需要筛选
            df = ak.stock_zh_a_spot_em()

            # 筛选出指定股票
            stock_data = df[df['代码'] == symbol.split('.')[0]]

            if stock_data.empty:
                raise DataProviderError(f"No quote data for {symbol}")

            row = stock_data.iloc[0]

            # 映射字段
            quote = {
                'symbol': symbol,
                'name': row['名称'],
                'date': datetime.now().strftime('%Y%m%d'),
                'open': float(row['今开']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'close': float(row['最新价']),
                'pre_close': float(row['昨收']),
                'change': float(row['涨跌额']),
                'pct_change': float(row['涨跌幅']),
                'volume': int(row['成交量']),
                'amount': float(row['成交额']),
                'turnover_rate': float(row.get('换手率', 0)),
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
        symbol_code = self._normalize_symbol(symbol).split('.')[0]
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')

        try:
            # 使用 AkShare 获取历史数据
            # period="daily" 日线数据，adjust="qfq" 前复权
            df = ak.stock_zh_a_hist(
                symbol=symbol_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )

            if df.empty:
                raise DataProviderError(f"No historical data for {symbol}")

            # 标准化列名（AkShare 返回的列名是中文）
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover_rate',
            })

            # 添加股票代码
            df['symbol'] = symbol

            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])

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
