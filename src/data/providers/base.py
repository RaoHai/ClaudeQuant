"""数据提供者抽象基类"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import pandas as pd


class DataProvider(ABC):
    """数据提供者抽象基类"""

    def __init__(self, config: dict = None):
        """
        初始化数据提供者

        Args:
            config: 配置字典
        """
        self.config = config or {}

    @abstractmethod
    def get_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            symbol: 股票代码 (e.g., '000001.SZ')
            start_date: 开始日期 (格式: 'YYYYMMDD' 或 'YYYY-MM-DD')
            end_date: 结束日期 (格式: 'YYYYMMDD' 或 'YYYY-MM-DD')

        Returns:
            DataFrame with columns: ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']
            日期格式: datetime
            已按日期升序排序
        """
        pass

    @abstractmethod
    def get_stock_list(self, market: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票列表

        Args:
            market: 市场代码 ('SH', 'SZ', 'BJ')，None 表示所有市场

        Returns:
            DataFrame with columns: ['symbol', 'name', 'market', 'list_date', ...]
        """
        pass

    def get_minute_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: str = '1min'
    ) -> pd.DataFrame:
        """
        获取分钟线数据（可选实现）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 频率 ('1min', '5min', '15min', '30min', '60min')

        Returns:
            DataFrame with columns: ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support minute data")

    def normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码

        Args:
            symbol: 原始股票代码 (可能是 '000001' 或 '000001.SZ')

        Returns:
            标准化后的代码 (e.g., '000001.SZ')
        """
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

    def normalize_date(self, date: str) -> str:
        """
        标准化日期格式为 YYYYMMDD

        Args:
            date: 日期字符串 ('YYYYMMDD' 或 'YYYY-MM-DD')

        Returns:
            YYYYMMDD 格式的日期
        """
        if '-' in date:
            return date.replace('-', '')
        return date

    def parse_date(self, date: str) -> datetime:
        """
        解析日期字符串为 datetime

        Args:
            date: 日期字符串

        Returns:
            datetime 对象
        """
        if len(date) == 8:  # YYYYMMDD
            return datetime.strptime(date, '%Y%m%d')
        else:  # YYYY-MM-DD
            return datetime.strptime(date, '%Y-%m-%d')

    def validate_dataframe(self, df: pd.DataFrame, required_columns: List[str]) -> None:
        """
        验证 DataFrame 包含必需的列

        Args:
            df: DataFrame
            required_columns: 必需的列名列表

        Raises:
            ValueError: 如果缺少必需的列
        """
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame missing required columns: {missing}")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
