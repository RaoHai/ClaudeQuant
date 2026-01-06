"""CLI 主入口"""

import click
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx, debug):
    """ClaudeQuant - A股量化交易平台"""
    # 设置日志
    config = get_config()
    log_level = 'DEBUG' if debug else config.get_log_level()
    setup_logger(log_level=log_level, console_output=True)

    # 将配置存入上下文
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['debug'] = debug

    logger.info("ClaudeQuant CLI started")


# 导入子命令
from src.cli.data_cmd import data
from src.cli.backtest_cmd import backtest

cli.add_command(data)
cli.add_command(backtest)


@cli.command()
def version():
    """显示版本信息"""
    click.echo("ClaudeQuant v0.1.0")
    click.echo("A-share quantitative trading platform powered by Claude Code")


if __name__ == '__main__':
    cli(obj={})
