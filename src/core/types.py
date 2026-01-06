"""ClaudeQuant 类型定义"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import pandas as pd


class OrderSide(str, Enum):
    """订单方向"""
    BUY = 'BUY'
    SELL = 'SELL'


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = 'PENDING'  # 待成交
    FILLED = 'FILLED'  # 已成交
    CANCELLED = 'CANCELLED'  # 已取消
    REJECTED = 'REJECTED'  # 已拒绝


class SignalAction(str, Enum):
    """信号动作"""
    BUY = 'BUY'
    SELL = 'SELL'
    HOLD = 'HOLD'


@dataclass
class Signal:
    """交易信号"""
    action: SignalAction
    symbol: str
    price: float
    quantity: int
    timestamp: datetime
    reason: str = ""  # 信号原因（用于报告）
    confidence: float = 1.0  # 信号置信度 [0-1]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (f"Signal({self.action.value} {self.quantity} shares of {self.symbol} "
                f"at {self.price:.2f}, reason: {self.reason})")


@dataclass
class Order:
    """订单"""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float  # 限价单价格
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_price: float = 0.0
    commission: float = 0.0
    created_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED

    @property
    def filled_amount(self) -> float:
        """成交金额（不含手续费）"""
        return self.filled_quantity * self.filled_price

    def __str__(self) -> str:
        return (f"Order({self.order_id}: {self.side.value} {self.quantity} "
                f"{self.symbol} @ {self.price:.2f}, status={self.status.value})")


@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: int  # 持仓数量
    avg_cost: float  # 平均成本
    current_price: float = 0.0  # 当前价格
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """成本总额"""
        return self.quantity * self.avg_cost

    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_pct(self) -> float:
        """未实现盈亏百分比"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

    def update_price(self, price: float):
        """更新当前价格"""
        self.current_price = price
        self.last_updated = datetime.now()

    def add(self, quantity: int, price: float):
        """增加持仓"""
        total_cost = self.cost_basis + (quantity * price)
        self.quantity += quantity
        self.avg_cost = total_cost / self.quantity if self.quantity > 0 else 0.0
        self.last_updated = datetime.now()

    def reduce(self, quantity: int) -> float:
        """减少持仓，返回实现盈亏"""
        if quantity > self.quantity:
            raise ValueError(f"Cannot reduce {quantity} shares, only have {self.quantity}")

        realized_pnl = quantity * (self.current_price - self.avg_cost)
        self.quantity -= quantity
        self.last_updated = datetime.now()
        return realized_pnl

    def __str__(self) -> str:
        return (f"Position({self.symbol}: {self.quantity} shares @ avg {self.avg_cost:.2f}, "
                f"current {self.current_price:.2f}, PnL: {self.unrealized_pnl:+.2f} "
                f"({self.unrealized_pnl_pct:+.2f}%))")


@dataclass
class Trade:
    """成交记录"""
    trade_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    commission: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def amount(self) -> float:
        """成交金额（不含手续费）"""
        return self.quantity * self.price

    @property
    def total_cost(self) -> float:
        """总成本（含手续费）"""
        return self.amount + self.commission

    def __str__(self) -> str:
        return (f"Trade({self.trade_id}: {self.side.value} {self.quantity} "
                f"{self.symbol} @ {self.price:.2f}, commission: {self.commission:.2f})")


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float

    # 时间序列数据
    portfolio_values: pd.Series  # 每日资产价值
    returns: pd.Series  # 每日收益率
    benchmark_returns: Optional[pd.Series] = None  # 基准收益率

    # 交易记录
    orders: list = field(default_factory=list)
    trades: list = field(default_factory=list)

    # 性能指标
    metrics: Dict[str, float] = field(default_factory=dict)

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_return(self) -> float:
        """总收益率"""
        return (self.final_capital - self.initial_capital) / self.initial_capital

    @property
    def total_return_pct(self) -> float:
        """总收益率百分比"""
        return self.total_return * 100

    def __str__(self) -> str:
        return (f"BacktestResult({self.strategy_name} on {self.symbol}: "
                f"Return {self.total_return_pct:+.2f}%, "
                f"Sharpe {self.metrics.get('sharpe_ratio', 0):.2f})")
