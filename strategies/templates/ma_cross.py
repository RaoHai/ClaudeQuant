"""双均线策略（MA Cross Strategy）"""

from typing import Optional
import pandas as pd

from src.strategy.base import Strategy
from src.strategy.indicators import calculate_ma, calculate_crossover
from src.core.types import Signal, SignalAction
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MACrossStrategy(Strategy):
    """
    双均线策略

    策略逻辑:
    - 快线上穿慢线 -> 买入信号（金叉）
    - 快线下穿慢线 -> 卖出信号（死叉）

    参数:
    - fast_period: 快线周期（默认 5）
    - slow_period: 慢线周期（默认 20）
    - position_size: 仓位比例（默认 1.0，即满仓）
    """

    def __init__(self, params: dict = None):
        default_params = {
            'fast_period': 5,
            'slow_period': 20,
            'position_size': 1.0  # 满仓
        }

        if params:
            default_params.update(params)

        super().__init__(default_params)

        self.fast_period = self.params['fast_period']
        self.slow_period = self.params['slow_period']
        self.position_size = self.params['position_size']

        logger.info(f"MACrossStrategy: fast={self.fast_period}, slow={self.slow_period}")

    def init(self, data: pd.DataFrame) -> None:
        """
        初始化策略 - 计算双均线指标
        """
        self.data = data.copy()

        # 计算快慢均线
        self.data['ma_fast'] = calculate_ma(self.data['close'], self.fast_period)
        self.data['ma_slow'] = calculate_ma(self.data['close'], self.slow_period)

        # 计算交叉信号
        self.data['crossover'] = calculate_crossover(
            self.data['ma_fast'],
            self.data['ma_slow']
        )

        logger.info(f"Indicators calculated for {len(self.data)} bars")

    def next(self, bar: pd.Series) -> Optional[Signal]:
        """
        处理每个bar，生成交易信号
        """
        # 检查数据有效性
        if pd.isna(bar['ma_fast']) or pd.isna(bar['ma_slow']):
            return None

        crossover_signal = bar['crossover']

        # 金叉 - 买入信号
        if crossover_signal == 1 and self.current_position == 0:
            # 计算买入数量（简化版：使用固定数量）
            quantity = 100  # 买入100股（1手）

            signal = self.create_signal(
                action=SignalAction.BUY,
                price=bar['close'],
                quantity=quantity,
                reason=f"Golden Cross: MA{self.fast_period} crosses above MA{self.slow_period}",
                confidence=1.0
            )

            logger.info(f"BUY signal generated: {signal}")
            return signal

        # 死叉 - 卖出信号
        elif crossover_signal == -1 and self.current_position > 0:
            # 卖出所有持仓
            quantity = self.current_position

            signal = self.create_signal(
                action=SignalAction.SELL,
                price=bar['close'],
                quantity=quantity,
                reason=f"Death Cross: MA{self.fast_period} crosses below MA{self.slow_period}",
                confidence=1.0
            )

            logger.info(f"SELL signal generated: {signal}")
            return signal

        # 无信号
        return None

    def __str__(self) -> str:
        return f"MACrossStrategy(fast={self.fast_period}, slow={self.slow_period})"
