"""数据存储模块（Parquet 格式）"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd

from src.core.exceptions import DataError, DataNotFoundError
from src.core.constants import STD_COLUMNS
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataStorage:
    """Parquet 数据存储"""

    def __init__(self, data_dir: str = './data/market'):
        """
        初始化数据存储

        Args:
            data_dir: 数据目录
        """
        self.data_dir = Path(data_dir)
        self.daily_dir = self.data_dir / 'daily'
        self.minute_dir = self.data_dir / 'minute'

        # 确保目录存在
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self.minute_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Data storage initialized: {self.data_dir}")

    def save_daily_data(self, symbol: str, data: pd.DataFrame) -> None:
        """
        保存日线数据

        Args:
            symbol: 股票代码
            data: DataFrame (必须包含标准列)
        """
        if data.empty:
            logger.warning(f"Empty dataframe for {symbol}, skip saving")
            return

        # 验证必需列
        required_cols = ['symbol', 'date', 'open', 'high', 'low', 'close']
        missing = set(required_cols) - set(data.columns)
        if missing:
            raise DataError(f"DataFrame missing columns: {missing}")

        # 确保日期是 datetime 类型
        if not pd.api.types.is_datetime64_any_dtype(data['date']):
            data['date'] = pd.to_datetime(data['date'])

        # 按日期排序
        data = data.sort_values('date').reset_index(drop=True)

        # 保存为 Parquet
        file_path = self.daily_dir / f"{symbol.replace('.', '_')}.parquet"
        data.to_parquet(file_path, engine='pyarrow', compression='snappy', index=False)

        logger.info(f"Saved {len(data)} bars to {file_path}")

    def load_daily_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        加载日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)

        Returns:
            DataFrame
        """
        file_path = self.daily_dir / f"{symbol.replace('.', '_')}.parquet"

        if not file_path.exists():
            raise DataNotFoundError(f"Data file not found: {file_path}")

        # 读取 Parquet
        df = pd.read_parquet(file_path, engine='pyarrow')

        # 确保日期是 datetime
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        # 日期过滤
        if start_date:
            start_dt = pd.to_datetime(start_date)
            df = df[df['date'] >= start_dt]

        if end_date:
            end_dt = pd.to_datetime(end_date)
            df = df[df['date'] <= end_dt]

        logger.info(f"Loaded {len(df)} bars for {symbol}")
        return df

    def has_daily_data(self, symbol: str) -> bool:
        """检查是否已有数据"""
        file_path = self.daily_dir / f"{symbol.replace('.', '_')}.parquet"
        return file_path.exists()

    def get_data_date_range(self, symbol: str) -> Optional[tuple]:
        """
        获取已有数据的日期范围

        Args:
            symbol: 股票代码

        Returns:
            (start_date, end_date) 或 None
        """
        if not self.has_daily_data(symbol):
            return None

        df = self.load_daily_data(symbol)
        if df.empty:
            return None

        return (df['date'].min(), df['date'].max())

    def update_daily_data(self, symbol: str, new_data: pd.DataFrame) -> None:
        """
        更新日线数据（增量更新）

        Args:
            symbol: 股票代码
            new_data: 新数据
        """
        if new_data.empty:
            logger.warning(f"No new data to update for {symbol}")
            return

        # 如果已有数据，合并
        if self.has_daily_data(symbol):
            existing = self.load_daily_data(symbol)

            # 合并并去重
            combined = pd.concat([existing, new_data], ignore_index=True)
            combined = combined.drop_duplicates(subset=['symbol', 'date'], keep='last')
            combined = combined.sort_values('date').reset_index(drop=True)

            self.save_daily_data(symbol, combined)
            logger.info(f"Updated data for {symbol}: added {len(new_data)} new bars")
        else:
            # 直接保存
            self.save_daily_data(symbol, new_data)

    def list_symbols(self) -> list:
        """列出所有已存储的股票代码"""
        symbols = []
        for file_path in self.daily_dir.glob('*.parquet'):
            # 从文件名恢复股票代码
            symbol = file_path.stem.replace('_', '.')
            symbols.append(symbol)
        return sorted(symbols)

    def delete_symbol_data(self, symbol: str) -> None:
        """删除股票数据"""
        file_path = self.daily_dir / f"{symbol.replace('.', '_')}.parquet"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted data for {symbol}")
        else:
            logger.warning(f"No data file found for {symbol}")

    def get_storage_stats(self) -> dict:
        """获取存储统计信息"""
        symbols = self.list_symbols()
        total_files = len(symbols)

        total_size = 0
        for file_path in self.daily_dir.glob('*.parquet'):
            total_size += file_path.stat().st_size

        return {
            'total_symbols': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'data_dir': str(self.data_dir)
        }
