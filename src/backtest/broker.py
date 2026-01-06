"""模拟券商（订单撮合、手续费计算）"""

from datetime import datetime
from typing import List, Optional
import uuid

from src.core.types import Order, OrderSide, OrderStatus, Trade
from src.core.exceptions import InsufficientFundsError, InvalidOrderError
from src.core.constants import DEFAULT_COMMISSION_RATE, DEFAULT_MIN_COMMISSION, DEFAULT_STAMP_TAX
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Broker:
    """模拟券商"""

    def __init__(
        self,
        initial_capital: float,
        commission_rate: float = DEFAULT_COMMISSION_RATE,
        min_commission: float = DEFAULT_MIN_COMMISSION,
        stamp_tax: float = DEFAULT_STAMP_TAX,
        slippage: float = 0.0
    ):
        """
        初始化模拟券商

        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率
            min_commission: 最低手续费
            stamp_tax: 印花税（卖出时收取）
            slippage: 滑点
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.stamp_tax = stamp_tax
        self.slippage = slippage

        self.orders: List[Order] = []
        self.trades: List[Trade] = []

        logger.info(f"Broker initialized: capital={initial_capital}, "
                   f"commission={commission_rate}, slippage={slippage}")

    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float
    ) -> Order:
        """
        提交订单

        Args:
            symbol: 股票代码
            side: 买卖方向
            quantity: 数量
            price: 价格

        Returns:
            Order 对象
        """
        # 验证订单
        if quantity <= 0:
            raise InvalidOrderError(f"Invalid quantity: {quantity}")

        if price <= 0:
            raise InvalidOrderError(f"Invalid price: {price}")

        # 创建订单
        order = Order(
            order_id=self._generate_order_id(),
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING,
            created_at=datetime.now()
        )

        # 如果是买单，检查资金是否充足
        if side == OrderSide.BUY:
            total_cost = self._calculate_buy_cost(quantity, price)
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                logger.warning(f"Order rejected: insufficient funds. "
                             f"Need {total_cost:.2f}, have {self.cash:.2f}")
                raise InsufficientFundsError(
                    f"Insufficient funds: need {total_cost:.2f}, have {self.cash:.2f}"
                )

        self.orders.append(order)
        logger.debug(f"Order submitted: {order}")

        return order

    def fill_order(self, order: Order, fill_price: Optional[float] = None) -> Trade:
        """
        成交订单

        Args:
            order: 订单
            fill_price: 成交价（None 则使用订单价格）

        Returns:
            Trade 对象
        """
        if order.status != OrderStatus.PENDING:
            raise InvalidOrderError(f"Order is not pending: {order.status}")

        # 计算成交价（含滑点）
        if fill_price is None:
            fill_price = order.price

        if order.side == OrderSide.BUY:
            actual_price = fill_price * (1 + self.slippage)
        else:  # SELL
            actual_price = fill_price * (1 - self.slippage)

        # 计算手续费
        commission = self._calculate_commission(order.quantity, actual_price, order.side)

        # 更新订单状态
        order.filled_quantity = order.quantity
        order.filled_price = actual_price
        order.commission = commission
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()

        # 更新现金
        if order.side == OrderSide.BUY:
            total_cost = order.filled_amount + commission
            self.cash -= total_cost
            logger.debug(f"BUY filled: cost={total_cost:.2f}, cash={self.cash:.2f}")

        else:  # SELL
            # 卖出需要额外计算印花税
            stamp_tax_amount = order.filled_amount * self.stamp_tax
            total_received = order.filled_amount - commission - stamp_tax_amount
            self.cash += total_received
            logger.debug(f"SELL filled: received={total_received:.2f}, cash={self.cash:.2f}")

        # 创建成交记录
        trade = Trade(
            trade_id=self._generate_trade_id(),
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.filled_quantity,
            price=actual_price,
            commission=commission,
            timestamp=order.filled_at
        )

        self.trades.append(trade)
        logger.info(f"Trade executed: {trade}")

        return trade

    def _calculate_commission(self, quantity: int, price: float, side: OrderSide) -> float:
        """
        计算手续费

        Args:
            quantity: 数量
            price: 价格
            side: 买卖方向

        Returns:
            手续费金额
        """
        amount = quantity * price
        commission = amount * self.commission_rate

        # 不低于最低手续费
        commission = max(commission, self.min_commission)

        return commission

    def _calculate_buy_cost(self, quantity: int, price: float) -> float:
        """计算买入所需资金（含手续费）"""
        amount = quantity * price
        commission = self._calculate_commission(quantity, price, OrderSide.BUY)
        return amount + commission

    def _generate_order_id(self) -> str:
        """生成订单 ID"""
        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def _generate_trade_id(self) -> str:
        """生成成交 ID"""
        return f"TRD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def get_cash(self) -> float:
        """获取当前现金"""
        return self.cash

    def get_total_commission(self) -> float:
        """获取总手续费"""
        return sum(trade.commission for trade in self.trades)

    def get_trade_count(self) -> int:
        """获取成交次数"""
        return len(self.trades)

    def __str__(self) -> str:
        return f"Broker(cash={self.cash:.2f}, trades={len(self.trades)})"
