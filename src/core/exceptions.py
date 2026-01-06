"""ClaudeQuant 异常定义"""


class ClaudeQuantException(Exception):
    """ClaudeQuant 基础异常"""
    pass


class DataError(ClaudeQuantException):
    """数据相关异常"""
    pass


class DataNotFoundError(DataError):
    """数据未找到"""
    pass


class DataProviderError(DataError):
    """数据提供者异常"""
    pass


class DataValidationError(DataError):
    """数据验证失败"""
    pass


class StrategyError(ClaudeQuantException):
    """策略相关异常"""
    pass


class StrategyInitError(StrategyError):
    """策略初始化失败"""
    pass


class InvalidSignalError(StrategyError):
    """无效信号"""
    pass


class BacktestError(ClaudeQuantException):
    """回测相关异常"""
    pass


class InsufficientFundsError(BacktestError):
    """资金不足"""
    pass


class InvalidOrderError(BacktestError):
    """无效订单"""
    pass


class OrderRejectedError(BacktestError):
    """订单被拒绝"""
    pass


class TradingError(ClaudeQuantException):
    """交易相关异常"""
    pass


class InvalidPositionError(TradingError):
    """无效持仓"""
    pass


class AccountError(TradingError):
    """账户异常"""
    pass


class ConfigError(ClaudeQuantException):
    """配置相关异常"""
    pass


class ConfigNotFoundError(ConfigError):
    """配置未找到"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证失败"""
    pass
