"""数据提供者包"""

from .base import DataProvider
from .tushare import TushareProvider

__all__ = [
    'DataProvider',
    'TushareProvider',
]
