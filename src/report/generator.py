"""Markdown 分析报告生成器"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """分析报告生成器"""

    def __init__(self, output_dir: str = './reports'):
        """初始化"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_portfolio_report(
        self,
        quotes: List[Dict],
        analyses: Dict[str, Dict],
        output_file: str = None
    ) -> str:
        """
        生成持仓分析报告

        Args:
            quotes: 行情列表
            analyses: 技术分析结果字典 {symbol: analysis}
            output_file: 输出文件名

        Returns:
            报告文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"portfolio_analysis_{timestamp}.md"

        output_path = self.output_dir / output_file

        content = self._generate_markdown(quotes, analyses)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 同时创建 latest.md
        latest_path = self.output_dir / 'latest.md'
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Report generated: {output_path}")

        return str(output_path)

    def _generate_markdown(self, quotes: List[Dict], analyses: Dict[str, Dict]) -> str:
        """生成 Markdown 内容"""
        md = []

        # 标题
        md.append("# 持仓分析报告")
        md.append("")
        md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")

        # 持仓概况
        md.append("## 持仓概况")
        md.append("")
        md.append("| 代码 | 名称 | 最新价 | 涨跌幅 | 信号 |")
        md.append("|------|------|--------|--------|------|")

        for quote in quotes:
            symbol = quote['symbol']
            analysis = analyses.get(symbol, {})
            signal = analysis.get('signal', 'N/A')

            signal_emoji = {
                'buy': '🟢 买入',
                'sell': '🔴 卖出',
                'hold': '🟡 持有',
            }.get(signal, signal)

            md.append(
                f"| {symbol} | {quote['name']} | "
                f"¥{quote['close']:.2f} | "
                f"{quote['pct_change']:+.2f}% | "
                f"{signal_emoji} |"
            )

        md.append("")

        # 详细分析
        md.append("## 详细分析")
        md.append("")

        for quote in quotes:
            symbol = quote['symbol']
            analysis = analyses.get(symbol, {})

            if 'error' in analysis:
                md.append(f"### {quote['name']} ({symbol})")
                md.append("")
                md.append(f"**错误**: {analysis['error']}")
                md.append("")
                continue

            md.extend(self._generate_stock_analysis(quote, analysis))

        # 页脚
        md.append("---")
        md.append("")
        md.append("*由 ClaudeQuant AI 助手生成*")
        md.append("")
        md.append("**免责声明**: 本报告仅供参考，不构成投资建议。投资有风险，决策需谨慎。")
        md.append("")

        return '\n'.join(md)

    def _generate_stock_analysis(self, quote: Dict, analysis: Dict) -> List[str]:
        """生成单只股票的详细分析"""
        md = []

        symbol = quote['symbol']
        name = quote['name']

        md.append(f"### {name} ({symbol})")
        md.append("")

        # 行情数据
        md.append("#### 实时行情")
        md.append("")
        md.append(f"- **最新价**: ¥{quote['close']:.2f}")
        md.append(f"- **涨跌幅**: {quote['pct_change']:+.2f}%")
        md.append(f"- **涨跌额**: {quote['change']:+.2f}")
        md.append(f"- **开盘价**: ¥{quote['open']:.2f}")
        md.append(f"- **最高价**: ¥{quote['high']:.2f}")
        md.append(f"- **最低价**: ¥{quote['low']:.2f}")
        md.append(f"- **成交量**: {quote['volume'] / 100:,.0f} 手")
        md.append("")

        # 技术分析
        md.append("#### 技术指标分析")
        md.append("")

        # 均线
        if 'ma' in analysis:
            ma = analysis['ma']
            md.append("**均线系统**:")
            for key in ['ma5', 'ma10', 'ma20', 'ma60']:
                if key in ma:
                    data = ma[key]
                    position_text = "上方" if data['position'] == 'above' else "下方"
                    md.append(f"- {key.upper()}: ¥{data['value']:.2f} (当前价格在均线{position_text} {abs(data['distance_pct']):.2f}%)")

            if 'cross' in ma:
                if ma['cross'] == 'golden':
                    md.append("- **形态**: 🟢 金叉（看涨信号）")
                elif ma['cross'] == 'death':
                    md.append("- **形态**: 🔴 死叉（看跌信号）")

            md.append("")

        # MACD
        if 'macd' in analysis:
            macd = analysis['macd']
            trend_text = "多头" if macd.get('trend') == 'bullish' else "空头"
            md.append(f"**MACD**: {trend_text}趋势")
            md.append(f"- MACD: {macd['macd']:.4f}")
            md.append(f"- Signal: {macd['signal']:.4f}")
            md.append(f"- Histogram: {macd['histogram']:.4f}")

            if macd.get('cross') == 'golden':
                md.append("- **形态**: 🟢 金叉")
            elif macd.get('cross') == 'death':
                md.append("- **形态**: 🔴 死叉")

            md.append("")

        # RSI
        if 'rsi' in analysis:
            rsi = analysis['rsi']
            status_text = {
                'overbought': f"🔴 超买 (>{rsi['overbought_line']})",
                'oversold': f"🟢 超卖 (<{rsi['oversold_line']})",
                'normal': "🟡 正常"
            }.get(rsi['status'], rsi['status'])

            md.append(f"**RSI(14)**: {rsi['value']:.2f} - {status_text}")
            md.append("")

        # 布林带
        if 'bollinger' in analysis:
            bb = analysis['bollinger']
            position_text = {
                'above_upper': "🔴 突破上轨（超买区域）",
                'below_lower': "🟢 突破下轨（超卖区域）",
                'within': "🟡 在轨道内"
            }.get(bb['position'], bb['position'])

            md.append(f"**布林带**: {position_text}")
            md.append(f"- 上轨: ¥{bb['upper']:.2f}")
            md.append(f"- 中轨: ¥{bb['middle']:.2f}")
            md.append(f"- 下轨: ¥{bb['lower']:.2f}")
            md.append("")

        # 综合信号和建议
        signal = analysis.get('signal', 'hold')
        md.append("#### 综合评估")
        md.append("")

        if signal == 'buy':
            md.append("**信号**: 🟢 **买入信号**")
            md.append("")
            md.append("**操作建议**: 多个技术指标显示买入信号，可考虑逢低建仓或加仓。建议分批买入，控制仓位。")
        elif signal == 'sell':
            md.append("**信号**: 🔴 **卖出信号**")
            md.append("")
            md.append("**操作建议**: 多个技术指标显示卖出信号，建议减仓或止盈。如有盈利可考虑分批卖出。")
        else:
            md.append("**信号**: 🟡 **持有观望**")
            md.append("")
            md.append("**操作建议**: 当前技术指标无明显方向，建议持有观望，等待更明确的信号。")

        md.append("")
        md.append("---")
        md.append("")

        return md
