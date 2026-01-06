"""ClaudeQuant 日志工具"""

import sys
from pathlib import Path
from loguru import logger

from src.core.constants import LOG_DIR


def setup_logger(
    log_level: str = "INFO",
    log_file: str = "claudequant.log",
    rotation: str = "10 MB",
    retention: str = "30 days",
    console_output: bool = True
) -> None:
    """
    配置 loguru 日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件名
        rotation: 日志轮转大小
        retention: 日志保留时间
        console_output: 是否输出到控制台
    """
    # 移除默认的 handler
    logger.remove()

    # 添加控制台输出
    if console_output:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level=log_level,
            colorize=True
        )

    # 添加文件输出
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file

    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression="zip",  # 压缩旧日志
        encoding="utf-8"
    )

    logger.info(f"Logger initialized: level={log_level}, file={log_path}")


def get_logger(name: str = None):
    """
    获取日志器

    Args:
        name: 日志器名称（通常使用 __name__）

    Returns:
        logger 实例
    """
    if name:
        return logger.bind(name=name)
    return logger


# 便捷函数
def debug(message: str, **kwargs):
    """记录 DEBUG 日志"""
    logger.debug(message, **kwargs)


def info(message: str, **kwargs):
    """记录 INFO 日志"""
    logger.info(message, **kwargs)


def warning(message: str, **kwargs):
    """记录 WARNING 日志"""
    logger.warning(message, **kwargs)


def error(message: str, **kwargs):
    """记录 ERROR 日志"""
    logger.error(message, **kwargs)


def critical(message: str, **kwargs):
    """记录 CRITICAL 日志"""
    logger.critical(message, **kwargs)


def exception(message: str, **kwargs):
    """记录异常日志（包含堆栈跟踪）"""
    logger.exception(message, **kwargs)
