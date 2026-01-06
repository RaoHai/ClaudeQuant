"""数据加载器（统一数据访问接口）"""

from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from src.data.providers import DataProvider, TushareProvider
from src.data.storage import DataStorage
from src.core.exceptions import DataError, DataNotFoundError
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class DataLoader:
    """数据加载器（缓存优先，自动更新）"""

    def __init__(
        self,
        provider: Optional[DataProvider] = None,
        storage: Optional[DataStorage] = None,
        auto_update: bool = True
    ):
        """
        初始化数据加载器

        Args:
            provider: 数据提供者
            storage: 数据存储
            auto_update: 是否自动更新数据
        """
        self.config = get_config()
        self.auto_update = auto_update

        # 初始化存储
        if storage is None:
            data_dir = self.config.get_data_dir() / 'market'
            self.storage = DataStorage(str(data_dir))
        else:
            self.storage = storage

        # 初始化提供者
        if provider is None:
            provider_name = self.config.get_data_provider()
            if provider_name == 'tushare':
                import os
                token = os.getenv('TUSHARE_TOKEN')
                if not token:
                    raise DataError("TUSHARE_TOKEN environment variable not set")
                self.provider = TushareProvider(token)
            else:
                raise DataError(f"Unsupported data provider: {provider_name}")
        else:
            self.provider = provider

        logger.info(f"DataLoader initialized: provider={self.provider}, auto_update={auto_update}")

    def load_daily_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        加载日线数据（优先使用缓存）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            use_cache: 是否使用缓存

        Returns:
            DataFrame
        """
        # 标准化股票代码
        symbol = self.provider.normalize_symbol(symbol)

        # 转换日期
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        # 尝试从缓存加载
        if use_cache and self.storage.has_daily_data(symbol):
            logger.info(f"Loading data from cache: {symbol}")
            df = self.storage.load_daily_data(symbol, start_date, end_date)

            # 检查数据完整性
            if self._check_data_complete(df, start_dt, end_dt):
                logger.info(f"Cache hit: {symbol}, {len(df)} bars")
                return df
            else:
                logger.info(f"Cache incomplete, fetching from provider")

        # 从数据源获取
        logger.info(f"Fetching data from provider: {symbol}")
        df = self.provider.get_daily_bars(symbol, start_date, end_date)

        # 保存到缓存
        if use_cache:
            self.storage.update_daily_data(symbol, df)

        return df

    def _check_data_complete(self, df: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> bool:
        """
        检查数据是否完整

        Args:
            df: DataFrame
            start_dt: 期望的开始日期
            end_dt: 期望的结束日期

        Returns:
            是否完整
        """
        if df.empty:
            return False

        # 检查日期范围
        actual_start = df['date'].min()
        actual_end = df['date'].max()

        # 允许一定的误差（因为周末/节假日）
        start_ok = actual_start <= start_dt + timedelta(days=7)
        end_ok = actual_end >= end_dt - timedelta(days=7)

        return start_ok and end_ok

    def download_data(self, symbol: str, start_date: str, end_date: str) -> None:
        """
        下载并缓存数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        """
        symbol = self.provider.normalize_symbol(symbol)

        logger.info(f"Downloading data: {symbol} from {start_date} to {end_date}")

        df = self.provider.get_daily_bars(symbol, start_date, end_date)
        self.storage.save_daily_data(symbol, df)

        logger.info(f"Downloaded and saved {len(df)} bars for {symbol}")

    def update_data(self, symbol: str, days: int = 30) -> None:
        """
        更新数据（增量更新最近 N 天）

        Args:
            symbol: 股票代码
            days: 更新最近多少天的数据
        """
        symbol = self.provider.normalize_symbol(symbol)

        # 计算更新日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        logger.info(f"Updating data: {symbol} for last {days} days")

        df = self.provider.get_daily_bars(symbol, start_date, end_date)
        self.storage.update_daily_data(symbol, df)

        logger.info(f"Updated {len(df)} bars for {symbol}")

    def get_cached_symbols(self) -> list:
        """获取所有已缓存的股票代码"""
        return self.storage.list_symbols()

    def get_data_info(self, symbol: str) -> Optional[dict]:
        """
        获取数据信息

        Args:
            symbol: 股票代码

        Returns:
            数据信息字典或 None
        """
        symbol = self.provider.normalize_symbol(symbol)

        if not self.storage.has_daily_data(symbol):
            return None

        date_range = self.storage.get_data_date_range(symbol)
        if not date_range:
            return None

        df = self.storage.load_daily_data(symbol)

        return {
            'symbol': symbol,
            'start_date': date_range[0].strftime('%Y-%m-%d'),
            'end_date': date_range[1].strftime('%Y-%m-%d'),
            'total_bars': len(df),
            'file_exists': True
        }

    def clear_cache(self, symbol: str) -> None:
        """清除缓存"""
        symbol = self.provider.normalize_symbol(symbol)
        self.storage.delete_symbol_data(symbol)
        logger.info(f"Cleared cache for {symbol}")
