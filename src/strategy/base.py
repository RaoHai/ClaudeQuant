"""策略抽象基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd

from src.core.types import Signal, SignalAction, Order
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Strategy(ABC):
    """策略抽象基类"""

    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化策略

        Args:
            params: 策略参数字典
        """
        self.params = params or {}
        self.data: Optional[pd.DataFrame] = None
        self.current_position = 0  # 当前持仓
        self.current_index = 0  # 当前处理到的数据索引

        logger.info(f"{self.__class__.__name__} initialized with params: {self.params}")

    @abstractmethod
    def init(self, data: pd.DataFrame) -> None:
        """
        初始化策略（在回测开始前调用）

        在此方法中：
        - 计算技术指标
        - 预处理数据
        - 初始化策略状态

        Args:
            data: 历史数据 DataFrame
        """
        pass

    @abstractmethod
    def next(self, bar: pd.Series) -> Optional[Signal]:
        """
        处理新数据bar，生成交易信号

        在此方法中：
        - 分析当前市场状态
        - 根据策略逻辑生成买入/卖出/持有信号

        Args:
            bar: 当前数据行（包含 date, open, high, low, close, volume 等）

        Returns:
            Signal 对象或 None
        """
        pass

    def on_order_filled(self, order: Order) -> None:
        """
        订单成交回调（可选重写）

        Args:
            order: 已成交的订单
        """
        # 更新持仓
        if order.side.value == 'BUY':
            self.current_position += order.filled_quantity
        elif order.side.value == 'SELL':
            self.current_position -= order.filled_quantity

        logger.debug(f"Order filled: {order}, current position: {self.current_position}")

    def get_indicator(self, name: str) -> Optional[pd.Series]:
        """
        获取指标数据

        Args:
            name: 指标列名

        Returns:
            Series 或 None
        """
        if self.data is None or name not in self.data.columns:
            return None
        return self.data[name]

    def get_current_bar(self) -> Optional[pd.Series]:
        """获取当前bar"""
        if self.data is None or self.current_index >= len(self.data):
            return None
        return self.data.iloc[self.current_index]

    def get_previous_bar(self, n: int = 1) -> Optional[pd.Series]:
        """
        获取前 n 个bar

        Args:
            n: 向前偏移量

        Returns:
            Series 或 None
        """
        idx = self.current_index - n
        if self.data is None or idx < 0 or idx >= len(self.data):
            return None
        return self.data.iloc[idx]

    def get_historical_data(self, n: int) -> Optional[pd.DataFrame]:
        """
        获取最近 n 条历史数据

        Args:
            n: 数据条数

        Returns:
            DataFrame 或 None
        """
        if self.data is None:
            return None

        end_idx = self.current_index + 1
        start_idx = max(0, end_idx - n)

        if start_idx >= end_idx:
            return None

        return self.data.iloc[start_idx:end_idx]

    def create_signal(
        self,
        action: SignalAction,
        price: float,
        quantity: int,
        reason: str = "",
        confidence: float = 1.0
    ) -> Signal:
        """
        创建交易信号

        Args:
            action: 信号动作
            price: 价格
            quantity: 数量
            reason: 信号原因
            confidence: 置信度

        Returns:
            Signal 对象
        """
        bar = self.get_current_bar()
        symbol = bar['symbol'] if 'symbol' in bar else 'UNKNOWN'
        timestamp = bar['date'] if 'date' in bar else pd.Timestamp.now()

        return Signal(
            action=action,
            symbol=symbol,
            price=price,
            quantity=quantity,
            timestamp=timestamp,
            reason=reason,
            confidence=confidence
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(params={self.params})"
