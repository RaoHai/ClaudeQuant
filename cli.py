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
from src.market.fundamental import FundamentalAnalyzer
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
        click.echo(f"quote_data: {quote_data}")
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
@click.argument('symbol')
def fundamental(symbol):
    """基本面分析 - 资金面、机构持仓、政策面"""
    try:
        analyzer = FundamentalAnalyzer()
        analysis = analyzer.analyze_fundamental(symbol)

        click.echo(f"\n💰 **基本面分析: {symbol}**\n")

        # 资金流向
        if analysis['fund_flow']:
            fund = analysis['fund_flow']
            click.echo("【资金流向】")
            main_flow = fund.get('main_net_inflow', 0)
            main_flow_pct = fund.get('main_net_inflow_pct', 0)

            flow_icon = "📈" if main_flow > 0 else "📉"
            click.echo(f"  {flow_icon} 主力净流入: {main_flow / 10000:.2f} 万元 ({main_flow_pct:.2f}%)")

            click.echo(f"  超大单净流入: {fund.get('super_large_net_inflow', 0) / 10000:.2f} 万元")
            click.echo(f"  大单净流入: {fund.get('large_net_inflow', 0) / 10000:.2f} 万元")
            click.echo(f"  中单净流入: {fund.get('medium_net_inflow', 0) / 10000:.2f} 万元")
            click.echo(f"  小单净流入: {fund.get('small_net_inflow', 0) / 10000:.2f} 万元")
            click.echo("")

        # 股东持股
        if analysis['holder_info']:
            holder = analysis['holder_info']
            click.echo("【十大流通股东】")
            click.echo(f"  报告期: {holder.get('report_date', 'N/A')}")
            click.echo(f"  机构投资者: {holder.get('institutional_holders', 0)}/{holder.get('total_top10_holders', 0)} 席")
            click.echo(f"  前十大股东合计持股: {holder.get('total_holding_pct', 0):.2f}%")
            click.echo("")

            click.echo("  前5大股东:")
            for i, h in enumerate(holder.get('top_holders', []), 1):
                click.echo(f"    {i}. {h['name']}: {h['holding_pct']:.2f}%")
            click.echo("")

        # 股东增减持
        if analysis['holder_changes']:
            changes = analysis['holder_changes']
            net_change = changes.get('net_change_summary', 0)

            click.echo("【近期股东变动】")
            change_icon = "📈" if net_change > 0 else "📉" if net_change < 0 else "➡️"
            click.echo(f"  {change_icon} 净变化: {net_change:+.2f}%")
            click.echo("")

            click.echo("  最近变动:")
            for change in changes.get('recent_changes', [])[:5]:
                change_type = change['change_type']
                type_icon = "🟢" if change_type == '增持' else "🔴"
                click.echo(
                    f"    {type_icon} {change['date']} {change['holder_name'][:15]}: "
                    f"{change_type} {change['change_pct']:.2f}%"
                )
            click.echo("")

        # 综合评分
        if 'fundamental_rating' in analysis:
            rating = analysis['fundamental_rating']
            click.echo("【综合评分】")
            click.echo(f"  资金面评分: {rating['fund_score']:+.1f}")
            click.echo(f"  机构持仓评分: {rating['holder_score']:+.1f}")
            click.echo(f"  增减持评分: {rating['change_score']:+.1f}")
            click.echo(f"  总分: {rating['total_score']:.1f}")
            click.echo(f"  评级: **{rating['rating']}**")
            click.echo("")

    except Exception as e:
        click.echo(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('symbol')
def deep(symbol):
    """深度分析 - 挖掘隐藏信息、概念关联、对外投资"""
    try:
        analyzer = FundamentalAnalyzer()
        analysis = analyzer.analyze_deep(symbol)

        click.echo(f"\n🔍 **深度分析: {analysis['name']} ({symbol})**\n")

        # 所属概念板块
        if analysis['concepts']:
            click.echo("【概念板块】")
            concepts = analysis['concepts']
            click.echo(f"  共属于 {len(concepts)} 个概念板块")
            click.echo("")
            for i, concept in enumerate(concepts[:15], 1):  # 显示前15个
                click.echo(f"  {i}. {concept['name']}")
            if len(concepts) > 15:
                click.echo(f"  ... 还有 {len(concepts) - 15} 个概念")
            click.echo("")

        # 热点关键词
        hidden = analysis.get('hidden_info', {})
        if hidden.get('hot_keywords'):
            click.echo("【热点关键词】")
            keywords = hidden['hot_keywords']
            click.echo(f"  {', '.join(keywords)}")
            click.echo("")

        # 投资关联
        if hidden.get('investment_details'):
            click.echo("【关联企业/对外投资】🔥")
            click.echo("  从新闻中提取到以下投资/参股关系:")
            for i, inv in enumerate(hidden['investment_details'], 1):
                stake_info = f" (持股 {inv['stake']}%)" if inv['stake'] else ""
                click.echo(f"  {i}. {inv['name']}{stake_info}")
                click.echo(f"     来源: [{inv['date']}] {inv['source']}")
            click.echo("")
        elif hidden.get('investments'):
            click.echo("【关联企业/对外投资】")
            click.echo("  以下企业在新闻中被提及（可能是投资、参股或合作关系）:")
            for i, company in enumerate(hidden['investments'], 1):
                click.echo(f"  {i}. {company}")
            click.echo("")

        # 最新新闻
        if analysis['news']:
            click.echo("【最新新闻】")
            for i, news in enumerate(analysis['news'][:5], 1):
                click.echo(f"  {i}. [{news['date']}] {news['title']}")
            click.echo("")

        # 提示
        click.echo("💡 **投资线索**")
        if hidden.get('hot_keywords'):
            click.echo(f"  - 涉及热点: {', '.join(hidden['hot_keywords'])}")
        if hidden.get('investments'):
            click.echo(f"  - 发现 {len(hidden['investments'])} 个潜在关联企业")
        if analysis['concepts']:
            # 找出热门概念
            hot_concepts = ['航天', '卫星', '军工', 'AI', '新能源', '芯片', '半导体']
            matched = [c['name'] for c in analysis['concepts'] if any(hot in c['name'] for hot in hot_concepts)]
            if matched:
                click.echo(f"  - 热门概念: {', '.join(matched[:5])}")
        click.echo("")

    except Exception as e:
        click.echo(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
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
