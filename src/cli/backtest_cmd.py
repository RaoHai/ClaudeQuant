"""回测命令"""

import click
from rich.console import Console
from pathlib import Path
import sys

from src.data.loader import DataLoader
from src.backtest.engine import BacktestEngine
from src.backtest.report import ReportGenerator
from src.utils.logger import get_logger

# 导入策略
from strategies.templates.ma_cross import MACrossStrategy

console = Console()
logger = get_logger(__name__)

# 策略映射
STRATEGIES = {
    'ma_cross': MACrossStrategy,
}


@click.command()
@click.option('--strategy', '-st', required=True, help='策略名称 (ma_cross)')
@click.option('--symbol', '-s', required=True, help='股票代码')
@click.option('--start', required=True, help='回测开始日期 (YYYYMMDD or YYYY-MM-DD)')
@click.option('--end', required=True, help='回测结束日期 (YYYYMMDD or YYYY-MM-DD)')
@click.option('--params', '-p', help='策略参数 (格式: key1=value1,key2=value2)')
@click.option('--capital', '-c', type=float, help='初始资金')
@click.option('--output', '-o', help='报告输出文件名')
def backtest(strategy, symbol, start, end, params, capital, output):
    """运行策略回测"""
    console.print(f"[bold blue]Running backtest...[/bold blue]")
    console.print(f"  Strategy: {strategy}")
    console.print(f"  Symbol: {symbol}")
    console.print(f"  Period: {start} ~ {end}")

    try:
        # 1. 加载数据
        console.print("\n[bold]Step 1: Loading data...[/bold]")
        loader = DataLoader()
        symbol = loader.provider.normalize_symbol(symbol)

        data = loader.load_daily_data(symbol, start, end, use_cache=True)

        console.print(f"  Loaded {len(data)} bars")

        # 2. 初始化策略
        console.print("\n[bold]Step 2: Initializing strategy...[/bold]")

        if strategy not in STRATEGIES:
            console.print(f"[bold red]✗ Unknown strategy: {strategy}[/bold red]")
            console.print(f"  Available strategies: {', '.join(STRATEGIES.keys())}")
            return

        # 解析参数
        strategy_params = {}
        if params:
            for param in params.split(','):
                key, value = param.split('=')
                # 尝试转换为数字
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # 保持字符串
                strategy_params[key.strip()] = value

        strategy_class = STRATEGIES[strategy]
        strategy_instance = strategy_class(strategy_params)

        console.print(f"  Strategy initialized: {strategy_instance}")

        # 3. 运行回测
        console.print("\n[bold]Step 3: Running backtest...[/bold]")

        engine_kwargs = {}
        if capital:
            engine_kwargs['initial_capital'] = capital

        engine = BacktestEngine(**engine_kwargs)
        result = engine.run(strategy_instance, data, symbol)

        console.print(f"  Backtest completed!")

        # 4. 生成报告
        console.print("\n[bold]Step 4: Generating report...[/bold]")

        report_gen = ReportGenerator()
        report_path = report_gen.generate(result, output_file=output, include_charts=True)

        console.print(f"  Report saved to: {report_path}")

        # 5. 显示结果摘要
        console.print("\n[bold green]═══ Backtest Results ═══[/bold green]")
        console.print(f"  Total Return: [bold]{result.total_return_pct:+.2f}%[/bold]")
        console.print(f"  Annual Return: {result.metrics['annual_return'] * 100:+.2f}%")
        console.print(f"  Max Drawdown: {result.metrics['max_drawdown'] * 100:.2f}%")
        console.print(f"  Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}")
        console.print(f"  Total Trades: {len(result.trades)}")
        console.print(f"  Final Capital: ¥{result.final_capital:,.2f}")

        console.print(f"\n[bold green]✓ Backtest completed successfully![/bold green]")
        console.print(f"\nView full report: [cyan]{report_path}[/cyan]")

    except Exception as e:
        console.print(f"\n[bold red]✗ Backtest failed: {e}[/bold red]")
        logger.exception("Backtest failed")
        sys.exit(1)
