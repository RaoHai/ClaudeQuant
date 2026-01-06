#!/usr/bin/env python3
"""CLI 工具脚本"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import click
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.quote.provider import QuoteProvider
from src.analysis.analyzer import TechnicalAnalyzer
from src.report.generator import ReportGenerator
from src.utils.logger import setup_logger

# 设置日志
setup_logger(log_level=os.getenv('LOG_LEVEL', 'INFO'), console_output=False)


@click.group()
def cli():
    """ClaudeQuant CLI Tool"""
    pass


@cli.command()
def portfolio():
    """显示持仓概况"""
    try:
        # 读取持仓配置
        symbols_str = os.getenv('PORTFOLIO_SYMBOLS', '')
        if not symbols_str:
            click.echo("❌ 请在 .env 文件中配置 PORTFOLIO_SYMBOLS")
            return

        symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]

        # 获取行情
        provider = QuoteProvider()
        quotes = provider.get_portfolio_quotes(symbols)

        # 输出表格
        click.echo("\n📊 **持仓概况**\n")
        click.echo(f"{'代码':<12} {'名称':<10} {'最新价':>10} {'涨跌幅':>10}")
        click.echo("-" * 50)

        for quote in quotes:
            pct_change = quote['pct_change']
            pct_str = f"{pct_change:+.2f}%"

            click.echo(
                f"{quote['symbol']:<12} "
                f"{quote['name']:<10} "
                f"{quote['close']:>10.2f} "
                f"{pct_str:>10}"
            )

        click.echo("")

    except Exception as e:
        click.echo(f"❌ 错误: {e}")
        sys.exit(1)


@cli.command()
@click.argument('symbol')
def quote(symbol):
    """获取实时行情"""
    try:
        provider = QuoteProvider()
        quote_data = provider.get_realtime_quote(symbol)

        click.echo(f"\n📈 **{quote_data['name']} ({quote_data['symbol']})**\n")
        click.echo(f"最新价: ¥{quote_data['close']:.2f}")
        click.echo(f"涨跌幅: {quote_data['pct_change']:+.2f}%")
        click.echo(f"涨跌额: {quote_data['change']:+.2f}")
        click.echo(f"开盘价: ¥{quote_data['open']:.2f}")
        click.echo(f"最高价: ¥{quote_data['high']:.2f}")
        click.echo(f"最低价: ¥{quote_data['low']:.2f}")
        click.echo(f"成交量: {quote_data['volume'] / 100:,.0f} 手")
        click.echo(f"成交额: {quote_data['amount'] / 10000:,.2f} 万元")
        click.echo("")

    except Exception as e:
        click.echo(f"❌ 错误: {e}")
        sys.exit(1)


@cli.command()
@click.argument('symbol')
def technical(symbol):
    """技术分析"""
    try:
        # 获取历史数据
        provider = QuoteProvider()
        data = provider.get_historical_data(symbol, days=60)

        # 技术分析
        analyzer = TechnicalAnalyzer()
        analysis = analyzer.analyze(data)

        if 'error' in analysis:
            click.echo(f"❌ {analysis['error']}")
            return

        click.echo(f"\n📊 **技术分析: {symbol}**\n")

        # 当前价格
        click.echo(f"当前价格: ¥{analysis['current_price']:.2f}")
        click.echo(f"涨跌幅: {analysis['pct_change']:+.2f}%\n")

        # 均线
        if 'ma' in analysis:
            click.echo("均线系统:")
            for key in ['ma5', 'ma10', 'ma20', 'ma60']:
                if key in analysis['ma']:
                    ma_data = analysis['ma'][key]
                    pos_text = "↑" if ma_data['position'] == 'above' else "↓"
                    click.echo(f"  {key.upper()}: ¥{ma_data['value']:.2f} {pos_text}")

            if analysis['ma'].get('cross') == 'golden':
                click.echo("  🟢 金叉")
            elif analysis['ma'].get('cross') == 'death':
                click.echo("  🔴 死叉")
            click.echo("")

        # RSI
        if 'rsi' in analysis:
            rsi = analysis['rsi']
            status_map = {'overbought': '🔴 超买', 'oversold': '🟢 超卖', 'normal': '🟡 正常'}
            click.echo(f"RSI(14): {rsi['value']:.2f} - {status_map.get(rsi['status'], '')}\n")

        # 综合信号
        signal_map = {
            'buy': '🟢 买入信号',
            'sell': '🔴 卖出信号',
            'hold': '🟡 持有观望'
        }
        click.echo(f"综合信号: **{signal_map.get(analysis['signal'], analysis['signal'])}**\n")

    except Exception as e:
        click.echo(f"❌ 错误: {e}")
        sys.exit(1)


@cli.command()
def analyze():
    """生成完整分析报告"""
    try:
        # 读取持仓
        symbols_str = os.getenv('PORTFOLIO_SYMBOLS', '')
        if not symbols_str:
            click.echo("❌ 请在 .env 文件中配置 PORTFOLIO_SYMBOLS")
            return

        symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]

        click.echo("🔄 正在分析持仓...\n")

        # 获取行情
        provider = QuoteProvider()
        quotes = provider.get_portfolio_quotes(symbols)

        # 技术分析
        analyzer = TechnicalAnalyzer()
        analyses = {}

        for quote in quotes:
            symbol = quote['symbol']
            click.echo(f"  分析 {symbol}...")

            try:
                data = provider.get_historical_data(symbol, days=60)
                analysis = analyzer.analyze(data)
                analyses[symbol] = analysis
            except Exception as e:
                click.echo(f"    ⚠️ 分析失败: {e}")
                analyses[symbol] = {'error': str(e)}

        # 生成报告
        click.echo("\n📝 生成报告...")
        report_gen = ReportGenerator()
        report_path = report_gen.generate_portfolio_report(quotes, analyses)

        click.echo(f"\n✅ 报告已生成: {report_path}")
        click.echo(f"   查看报告: cat {report_path}\n")

    except Exception as e:
        click.echo(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
