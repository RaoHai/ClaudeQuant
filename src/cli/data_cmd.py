"""数据管理命令"""

import click
from rich.console import Console
from rich.table import Table

from src.data.loader import DataLoader
from src.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def data():
    """数据管理命令"""
    pass


@data.command()
@click.option('--symbol', '-s', required=True, help='股票代码 (e.g., 000001.SZ or 000001)')
@click.option('--start', required=True, help='开始日期 (YYYYMMDD or YYYY-MM-DD)')
@click.option('--end', required=True, help='结束日期 (YYYYMMDD or YYYY-MM-DD)')
@click.option('--force', is_flag=True, help='强制重新下载（忽略缓存）')
def download(symbol, start, end, force):
    """下载股票数据"""
    console.print(f"[bold blue]Downloading data for {symbol}...[/bold blue]")

    try:
        loader = DataLoader()

        # 标准化股票代码
        symbol = loader.provider.normalize_symbol(symbol)

        if force:
            # 清除缓存
            loader.clear_cache(symbol)

        # 下载数据
        loader.download_data(symbol, start, end)

        # 显示数据信息
        info = loader.get_data_info(symbol)

        console.print("[bold green]✓ Download completed![/bold green]")
        console.print(f"  Symbol: {info['symbol']}")
        console.print(f"  Date range: {info['start_date']} ~ {info['end_date']}")
        console.print(f"  Total bars: {info['total_bars']}")

    except Exception as e:
        console.print(f"[bold red]✗ Download failed: {e}[/bold red]")
        logger.exception("Download failed")


@data.command()
@click.option('--symbol', '-s', required=True, help='股票代码')
@click.option('--days', '-d', default=30, help='更新最近多少天的数据')
def update(symbol, days):
    """更新股票数据（增量）"""
    console.print(f"[bold blue]Updating data for {symbol}...[/bold blue]")

    try:
        loader = DataLoader()
        symbol = loader.provider.normalize_symbol(symbol)

        loader.update_data(symbol, days=days)

        info = loader.get_data_info(symbol)

        console.print("[bold green]✓ Update completed![/bold green]")
        console.print(f"  Symbol: {info['symbol']}")
        console.print(f"  Date range: {info['start_date']} ~ {info['end_date']}")
        console.print(f"  Total bars: {info['total_bars']}")

    except Exception as e:
        console.print(f"[bold red]✗ Update failed: {e}[/bold red]")
        logger.exception("Update failed")


@data.command()
@click.option('--symbol', '-s', help='股票代码（可选，不提供则列出所有）')
def info(symbol):
    """查看数据信息"""
    try:
        loader = DataLoader()

        if symbol:
            # 查看单个股票
            symbol = loader.provider.normalize_symbol(symbol)
            data_info = loader.get_data_info(symbol)

            if data_info is None:
                console.print(f"[yellow]No data found for {symbol}[/yellow]")
                return

            console.print(f"\n[bold]Data Info: {symbol}[/bold]")
            console.print(f"  Start date: {data_info['start_date']}")
            console.print(f"  End date: {data_info['end_date']}")
            console.print(f"  Total bars: {data_info['total_bars']}")

        else:
            # 列出所有股票
            symbols = loader.get_cached_symbols()

            if not symbols:
                console.print("[yellow]No cached data found[/yellow]")
                return

            table = Table(title="Cached Stocks")
            table.add_column("Symbol", style="cyan")
            table.add_column("Start Date", style="green")
            table.add_column("End Date", style="green")
            table.add_column("Bars", justify="right", style="magenta")

            for sym in symbols[:20]:  # 只显示前20个
                data_info = loader.get_data_info(sym)
                if data_info:
                    table.add_row(
                        data_info['symbol'],
                        data_info['start_date'],
                        data_info['end_date'],
                        str(data_info['total_bars'])
                    )

            console.print(table)

            if len(symbols) > 20:
                console.print(f"\n[dim]... and {len(symbols) - 20} more[/dim]")

    except Exception as e:
        console.print(f"[bold red]✗ Failed to get info: {e}[/bold red]")
        logger.exception("Info failed")


@data.command()
@click.option('--symbol', '-s', required=True, help='股票代码')
@click.option('--confirm', is_flag=True, help='确认删除')
def clear(symbol, confirm):
    """清除缓存数据"""
    if not confirm:
        console.print("[yellow]Use --confirm flag to confirm deletion[/yellow]")
        return

    try:
        loader = DataLoader()
        symbol = loader.provider.normalize_symbol(symbol)

        loader.clear_cache(symbol)

        console.print(f"[bold green]✓ Cache cleared for {symbol}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ Clear failed: {e}[/bold red]")
        logger.exception("Clear failed")
