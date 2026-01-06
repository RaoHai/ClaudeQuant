"""ClaudeQuant 配置管理"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

from src.core.exceptions import ConfigError, ConfigNotFoundError, ConfigValidationError


class Config:
    """配置管理器"""

    def __init__(self, config_dir: str = './config'):
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}

        # 加载环境变量
        load_dotenv()

        # 加载默认配置
        self.load_default_config()

    def load_default_config(self):
        """加载默认配置"""
        default_config_path = self.config_dir / 'default.yaml'
        if not default_config_path.exists():
            raise ConfigNotFoundError(f"Default config not found: {default_config_path}")

        with open(default_config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

    def load_config(self, config_path: str):
        """加载额外配置并合并"""
        path = Path(config_path)
        if not path.exists():
            raise ConfigNotFoundError(f"Config file not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            extra_config = yaml.safe_load(f)

        # 深度合并
        self._deep_merge(self._config, extra_config)

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        # 处理环境变量替换 ${VAR_NAME}
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            env_value = os.getenv(env_var)
            if env_value is None:
                return default
            return env_value

        return value

    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_data_dir(self) -> Path:
        """获取数据目录"""
        data_dir = self.get('system.data_dir', './data')
        return Path(data_dir)

    def get_report_dir(self) -> Path:
        """获取报告目录"""
        report_dir = self.get('system.report_dir', './reports')
        return Path(report_dir)

    def get_log_level(self) -> str:
        """获取日志级别"""
        # 优先从环境变量读取
        log_level = os.getenv('LOG_LEVEL')
        if log_level:
            return log_level
        return self.get('system.log_level', 'INFO')

    def get_data_provider(self) -> str:
        """获取数据提供者"""
        return self.get('data.provider', 'akshare')

    def get_initial_capital(self) -> float:
        """获取初始资金"""
        return float(self.get('backtest.initial_capital', 100000.0))

    def get_commission_rate(self) -> float:
        """获取手续费率"""
        return float(self.get('backtest.commission.stock', 0.0003))

    def get_min_commission(self) -> float:
        """获取最低手续费"""
        return float(self.get('backtest.commission.min_commission', 5.0))

    def get_slippage(self) -> float:
        """获取滑点"""
        return float(self.get('backtest.slippage', 0.0001))

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        value = self.get(key)
        if value is None:
            raise ConfigNotFoundError(f"Config key not found: {key}")
        return value

    def __contains__(self, key: str) -> bool:
        """支持 in 操作符"""
        return self.get(key) is not None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()


# 全局配置实例
_global_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def reset_config():
    """重置全局配置（主要用于测试）"""
    global _global_config
    _global_config = None
