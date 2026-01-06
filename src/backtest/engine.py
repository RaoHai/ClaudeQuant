"""回测引擎核心"""

from datetime import datetime
from typing import Dict, List
import pandas as pd

from src.strategy.base import Strategy
from src.backtest.broker import Broker
from src.core.types import BacktestResult, Signal, SignalAction, OrderSide, Position
from src.core.exceptions import BacktestError
from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class BacktestEngine:
    """事件驱动的回测引擎"""

    def __init__(
        self,
        initial_capital: float = None,
        commission_rate: float = None,
        min_commission: float = None,
        slippage: float = None
    ):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率
            min_commission: 最低手续费
            slippage: 滑点
        """
        config = get_config()

        self.initial_capital = initial_capital or config.get_initial_capital()
        self.commission_rate = commission_rate or config.get_commission_rate()
        self.min_commission = min_commission or config.get_min_commission()
        self.slippage = slippage or config.get_slippage()

        # 创建券商
        self.broker = Broker(
            initial_capital=self.initial_capital,
            commission_rate=self.commission_rate,
            min_commission=self.min_commission,
            slippage=self.slippage
        )

        # 持仓管理
        self.positions: Dict[str, Position] = {}

        # 回测结果记录
        self.portfolio_values: List[float] = []
        self.dates: List[datetime] = []

        logger.info(f"BacktestEngine initialized: capital={self.initial_capital}")

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        symbol: str
    ) -> BacktestResult:
        """
        运行回测

        Args:
            strategy: 策略实例
            data: 历史数据
            symbol: 股票代码

        Returns:
            BacktestResult
        """
        if data.empty:
            raise BacktestError("Data is empty")

        logger.info(f"Starting backtest: {strategy} on {symbol}, "
                   f"{len(data)} bars from {data['date'].min()} to {data['date'].max()}")

        # 策略初始化
        strategy.init(data)

        # 事件循环
        for idx in range(len(data)):
            bar = data.iloc[idx]
            strategy.current_index = idx

            # 更新持仓价格
            if symbol in self.positions:
                self.positions[symbol].update_price(bar['close'])

            # 生成信号
            signal = strategy.next(bar)

            # 处理信号
            if signal:
                self._process_signal(signal, bar)

            # 记录每日资产价值
            portfolio_value = self._calculate_portfolio_value(bar['close'])
            self.portfolio_values.append(portfolio_value)
            self.dates.append(bar['date'])

        # 生成回测结果
        result = self._generate_result(strategy, data, symbol)

        logger.info(f"Backtest completed: final_capital={result.final_capital:.2f}, "
                   f"return={result.total_return_pct:+.2f}%")

        return result

    def _process_signal(self, signal: Signal, bar: pd.Series):
        """处理交易信号"""
        symbol = signal.symbol

        if signal.action == SignalAction.BUY:
            try:
                order = self.broker.submit_order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    quantity=signal.quantity,
                    price=signal.price
                )

                # 立即成交（使用当前收盘价）
                trade = self.broker.fill_order(order, fill_price=bar['close'])

                # 更新持仓
                if symbol not in self.positions:
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=0,
                        avg_cost=0,
                        current_price=bar['close']
                    )

                self.positions[symbol].add(trade.quantity, trade.price)

                logger.info(f"BUY executed: {trade}, position: {self.positions[symbol]}")

            except Exception as e:
                logger.warning(f"Failed to execute BUY: {e}")

        elif signal.action == SignalAction.SELL:
            # 检查是否有持仓
            if symbol not in self.positions or self.positions[symbol].quantity == 0:
                logger.warning(f"No position to sell for {symbol}")
                return

            # 确定卖出数量
            sell_quantity = min(signal.quantity, self.positions[symbol].quantity)

            try:
                order = self.broker.submit_order(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=sell_quantity,
                    price=signal.price
                )

                # 立即成交
                trade = self.broker.fill_order(order, fill_price=bar['close'])

                # 更新持仓
                realized_pnl = self.positions[symbol].reduce(trade.quantity)

                logger.info(f"SELL executed: {trade}, realized PnL: {realized_pnl:+.2f}, "
                           f"position: {self.positions[symbol]}")

            except Exception as e:
                logger.warning(f"Failed to execute SELL: {e}")

    def _calculate_portfolio_value(self, current_price: float) -> float:
        """计算总资产价值"""
        cash = self.broker.get_cash()
        holdings_value = sum(pos.market_value for pos in self.positions.values())
        return cash + holdings_value

    def _generate_result(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        symbol: str
    ) -> BacktestResult:
        """生成回测结果"""
        # 创建时间序列
        portfolio_series = pd.Series(self.portfolio_values, index=self.dates)

        # 计算收益率
        returns = portfolio_series.pct_change().fillna(0)

        # 性能指标计算将在 metrics.py 中实现
        from src.backtest.metrics import MetricsCalculator
        metrics_calc = MetricsCalculator()
        metrics = metrics_calc.calculate_all(portfolio_series, returns)

        result = BacktestResult(
            strategy_name=strategy.__class__.__name__,
            symbol=symbol,
            start_date=data['date'].min().strftime('%Y-%m-%d'),
            end_date=data['date'].max().strftime('%Y-%m-%d'),
            initial_capital=self.initial_capital,
            final_capital=portfolio_series.iloc[-1] if len(portfolio_series) > 0 else self.initial_capital,
            portfolio_values=portfolio_series,
            returns=returns,
            orders=self.broker.orders,
            trades=self.broker.trades,
            metrics=metrics
        )

        return result

    def reset(self):
        """重置回测引擎"""
        self.broker = Broker(
            initial_capital=self.initial_capital,
            commission_rate=self.commission_rate,
            min_commission=self.min_commission,
            slippage=self.slippage
        )
        self.positions = {}
        self.portfolio_values = []
        self.dates = []
        logger.info("BacktestEngine reset")
