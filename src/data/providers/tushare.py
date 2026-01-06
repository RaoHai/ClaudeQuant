"""Tushare 数据提供者实现"""

import time
from typing import Optional
import pandas as pd
import tushare as ts

from src.data.providers.base import DataProvider
from src.core.exceptions import DataProviderError, DataNotFoundError
from src.core.constants import OHLCV_COLUMNS
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TushareProvider(DataProvider):
    """Tushare 数据提供者"""

    def __init__(self, token: str, config: dict = None):
        """
        初始化 Tushare 提供者

        Args:
            token: Tushare API Token
            config: 配置字典
        """
        super().__init__(config)

        if not token:
            raise DataProviderError("Tushare token is required")

        ts.set_token(token)
        self.pro = ts.pro_api()
        self.timeout = self.config.get('timeout', 30)
        self.retry = self.config.get('retry', 3)
        self.retry_delay = self.config.get('retry_delay', 1)

        logger.info("Tushare provider initialized")

    def _call_api(self, func, **kwargs):
        """
        调用 Tushare API（带重试）

        Args:
            func: API 函数
            **kwargs: 参数

        Returns:
            API 返回结果
        """
        for attempt in range(self.retry):
            try:
                result = func(**kwargs)
                return result
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.retry}): {e}")
                if attempt < self.retry - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise DataProviderError(f"Tushare API call failed: {e}")

    def get_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取日线数据"""
        # 标准化输入
        ts_code = self.normalize_symbol(symbol)
        start = self.normalize_date(start_date)
        end = self.normalize_date(end_date)

        logger.info(f"Fetching daily data: {ts_code} from {start} to {end}")

        # 调用 Tushare API
        df = self._call_api(
            self.pro.daily,
            ts_code=ts_code,
            start_date=start,
            end_date=end
        )

        if df is None or df.empty:
            raise DataNotFoundError(f"No data found for {ts_code} from {start} to {end}")

        # 数据清洗和标准化
        df = self._normalize_daily_data(df)

        logger.info(f"Fetched {len(df)} bars for {ts_code}")
        return df

    def _normalize_daily_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化日线数据"""
        # 重命名列
        df = df.rename(columns=OHLCV_COLUMNS)

        # 选择需要的列
        required_cols = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']
        df = df[required_cols]

        # 转换日期
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

        # 转换成交量和金额（Tushare: 手和千元 -> 股和元）
        df['volume'] = df['volume'] * 100  # 手 -> 股
        df['amount'] = df['amount'] * 1000  # 千元 -> 元

        # 按日期升序排序
        df = df.sort_values('date').reset_index(drop=True)

        return df

    def get_stock_list(self, market: Optional[str] = None) -> pd.DataFrame:
        """获取股票列表"""
        logger.info(f"Fetching stock list: market={market}")

        # 调用 Tushare API
        df = self._call_api(self.pro.stock_basic, exchange='', list_status='L')

        if df is None or df.empty:
            raise DataNotFoundError("Failed to fetch stock list")

        # 标准化
        df = df.rename(columns={
            'ts_code': 'symbol',
            'name': 'name',
            'area': 'area',
            'industry': 'industry',
            'market': 'market',
            'list_date': 'list_date'
        })

        # 筛选市场
        if market:
            market_upper = market.upper()
            df = df[df['symbol'].str.endswith(f'.{market_upper}')]

        logger.info(f"Fetched {len(df)} stocks")
        return df

    def get_minute_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: str = '1min'
    ) -> pd.DataFrame:
        """获取分钟线数据（需要 Tushare 高级权限）"""
        # 注意：Tushare 分钟数据需要一定积分权限
        raise NotImplementedError(
            "Minute data requires Tushare advanced permissions. "
            "Consider using AkShare for minute data."
        )
