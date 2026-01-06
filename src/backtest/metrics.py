"""性能指标计算模块"""

import numpy as np
import pandas as pd
from typing import Dict

from src.core.constants import TRADING_DAYS_PER_YEAR, RISK_FREE_RATE
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCalculator:
    """性能指标计算器"""

    def __init__(self, risk_free_rate: float = RISK_FREE_RATE):
        """
        初始化

        Args:
            risk_free_rate: 无风险利率（年化）
        """
        self.risk_free_rate = risk_free_rate

    def calculate_all(
        self,
        portfolio_values: pd.Series,
        returns: pd.Series
    ) -> Dict[str, float]:
        """
        计算所有性能指标

        Args:
            portfolio_values: 资产价值时间序列
            returns: 收益率时间序列

        Returns:
            指标字典
        """
        metrics = {}

        # 基础指标
        metrics['total_return'] = self.total_return(portfolio_values)
        metrics['annual_return'] = self.annual_return(portfolio_values)

        # 风险指标
        metrics['volatility'] = self.volatility(returns)
        metrics['max_drawdown'] = self.max_drawdown(portfolio_values)

        # 风险调整收益
        metrics['sharpe_ratio'] = self.sharpe_ratio(returns, self.risk_free_rate)
        metrics['sortino_ratio'] = self.sortino_ratio(returns, self.risk_free_rate)
        metrics['calmar_ratio'] = self.calmar_ratio(portfolio_values)

        # 交易统计
        metrics['trading_days'] = len(portfolio_values)

        logger.info(f"Metrics calculated: {metrics}")
        return metrics

    @staticmethod
    def total_return(portfolio_values: pd.Series) -> float:
        """
        总收益率

        Args:
            portfolio_values: 资产价值序列

        Returns:
            总收益率（小数形式）
        """
        if len(portfolio_values) == 0:
            return 0.0

        initial = portfolio_values.iloc[0]
        final = portfolio_values.iloc[-1]

        if initial == 0:
            return 0.0

        return (final - initial) / initial

    @staticmethod
    def annual_return(portfolio_values: pd.Series) -> float:
        """
        年化收益率

        Args:
            portfolio_values: 资产价值序列

        Returns:
            年化收益率（小数形式）
        """
        if len(portfolio_values) == 0:
            return 0.0

        total_ret = MetricsCalculator.total_return(portfolio_values)
        days = len(portfolio_values)

        if days == 0:
            return 0.0

        # 年化公式: (1 + total_return) ^ (252 / days) - 1
        annual_ret = (1 + total_ret) ** (TRADING_DAYS_PER_YEAR / days) - 1

        return annual_ret

    @staticmethod
    def volatility(returns: pd.Series, annualized: bool = True) -> float:
        """
        波动率（标准差）

        Args:
            returns: 收益率序列
            annualized: 是否年化

        Returns:
            波动率
        """
        if len(returns) == 0:
            return 0.0

        vol = returns.std()

        if annualized:
            vol *= np.sqrt(TRADING_DAYS_PER_YEAR)

        return vol

    @staticmethod
    def max_drawdown(portfolio_values: pd.Series) -> float:
        """
        最大回撤

        Args:
            portfolio_values: 资产价值序列

        Returns:
            最大回撤（正数，例如 0.15 表示 15%）
        """
        if len(portfolio_values) == 0:
            return 0.0

        # 计算累计最高价值
        cummax = portfolio_values.cummax()

        # 计算回撤
        drawdown = (portfolio_values - cummax) / cummax

        # 最大回撤
        max_dd = abs(drawdown.min())

        return max_dd

    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """
        夏普比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率（年化）

        Returns:
            夏普比率
        """
        if len(returns) == 0:
            return 0.0

        # 日收益率均值
        mean_return = returns.mean()

        # 波动率（日）
        std_return = returns.std()

        if std_return == 0:
            return 0.0

        # 日无风险收益率
        daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR

        # 夏普比率（年化）
        sharpe = (mean_return - daily_rf) / std_return * np.sqrt(TRADING_DAYS_PER_YEAR)

        return sharpe

    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> float:
        """
        索提诺比率（只考虑下行风险）

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率

        Returns:
            索提诺比率
        """
        if len(returns) == 0:
            return 0.0

        mean_return = returns.mean()

        # 下行偏差（只考虑负收益）
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return 0.0

        downside_std = downside_returns.std()

        if downside_std == 0:
            return 0.0

        daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR

        sortino = (mean_return - daily_rf) / downside_std * np.sqrt(TRADING_DAYS_PER_YEAR)

        return sortino

    @staticmethod
    def calmar_ratio(portfolio_values: pd.Series) -> float:
        """
        卡玛比率（年化收益率 / 最大回撤）

        Args:
            portfolio_values: 资产价值序列

        Returns:
            卡玛比率
        """
        annual_ret = MetricsCalculator.annual_return(portfolio_values)
        max_dd = MetricsCalculator.max_drawdown(portfolio_values)

        if max_dd == 0:
            return 0.0

        return annual_ret / max_dd

    @staticmethod
    def win_rate(trades: list) -> float:
        """
        胜率

        Args:
            trades: 交易列表

        Returns:
            胜率 (0-1)
        """
        if len(trades) == 0:
            return 0.0

        # 这里简化处理，实际需要配对买卖单计算盈亏
        # TODO: 完善交易配对逻辑

        return 0.0
