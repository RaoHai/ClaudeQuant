"""Markdown 回测报告生成器"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import matplotlib
matplotlib.use('Agg')  # 无 GUI 后端
import matplotlib.pyplot as plt
import pandas as pd

from src.core.types import BacktestResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Markdown 回测报告生成器"""

    def __init__(self, output_dir: str = './reports/backtest'):
        """
        初始化

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        result: BacktestResult,
        output_file: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """
        生成 Markdown 报告

        Args:
            result: 回测结果
            output_file: 输出文件名（不含路径）
            include_charts: 是否包含图表

        Returns:
            报告文件路径
        """
        # 生成文件名
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"backtest_{result.symbol.replace('.', '_')}_{timestamp}.md"

        output_path = self.output_dir / output_file

        logger.info(f"Generating report: {output_path}")

        # 生成 Markdown 内容
        content = self._generate_markdown(result, include_charts)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 生成图表
        if include_charts:
            self._generate_charts(result, output_path.stem)

        logger.info(f"Report generated: {output_path}")

        # 同时创建一个 latest.md 链接
        latest_path = self.output_dir / 'latest.md'
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    def _generate_markdown(self, result: BacktestResult, include_charts: bool) -> str:
        """生成 Markdown 内容"""
        md = []

        # 标题
        md.append(f"# 回测报告 - {result.strategy_name}")
        md.append("")

        # 基本信息
        md.append("## 基本信息")
        md.append("")
        md.append(f"- **策略名称**: {result.strategy_name}")
        md.append(f"- **股票代码**: {result.symbol}")
        md.append(f"- **回测区间**: {result.start_date} ~ {result.end_date}")
        md.append(f"- **初始资金**: ¥{result.initial_capital:,.2f}")
        md.append(f"- **最终资金**: ¥{result.final_capital:,.2f}")
        md.append("")

        # 收益统计
        md.append("## 收益统计")
        md.append("")
        md.append("| 指标 | 数值 |")
        md.append("|------|------|")
        md.append(f"| 总收益率 | {result.total_return_pct:+.2f}% |")
        md.append(f"| 年化收益率 | {result.metrics.get('annual_return', 0) * 100:+.2f}% |")
        md.append(f"| 最大回撤 | {result.metrics.get('max_drawdown', 0) * 100:.2f}% |")
        md.append(f"| 波动率（年化） | {result.metrics.get('volatility', 0) * 100:.2f}% |")
        md.append(f"| 夏普比率 | {result.metrics.get('sharpe_ratio', 0):.2f} |")
        md.append(f"| 索提诺比率 | {result.metrics.get('sortino_ratio', 0):.2f} |")
        md.append(f"| 卡玛比率 | {result.metrics.get('calmar_ratio', 0):.2f} |")
        md.append("")

        # 交易统计
        buy_count = sum(1 for o in result.orders if o.side.value == 'BUY' and o.is_filled)
        sell_count = sum(1 for o in result.orders if o.side.value == 'SELL' and o.is_filled)
        total_commission = sum(t.commission for t in result.trades)

        md.append("## 交易统计")
        md.append("")
        md.append(f"- 总交易次数: {len(result.trades)} 次")
        md.append(f"- 买入次数: {buy_count} 次")
        md.append(f"- 卖出次数: {sell_count} 次")
        md.append(f"- 总手续费: ¥{total_commission:,.2f}")
        md.append(f"- 交易天数: {result.metrics.get('trading_days', 0)} 天")
        md.append("")

        # 图表
        if include_charts:
            md.append("## 资金曲线")
            md.append("")
            chart_filename = f"{result.symbol.replace('.', '_')}_equity.png"
            md.append(f"![资金曲线](./{chart_filename})")
            md.append("")

            md.append("## 回撤曲线")
            md.append("")
            dd_filename = f"{result.symbol.replace('.', '_')}_drawdown.png"
            md.append(f"![回撤曲线](./{dd_filename})")
            md.append("")

        # 交易明细（仅显示最近 20 条）
        if result.trades:
            md.append("## 交易明细（最近20条）")
            md.append("")
            md.append("| 时间 | 操作 | 价格 | 数量 | 金额 | 手续费 |")
            md.append("|------|------|------|------|------|--------|")

            for trade in result.trades[-20:]:
                md.append(
                    f"| {trade.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                    f"{trade.side.value} | "
                    f"¥{trade.price:.2f} | "
                    f"{trade.quantity} | "
                    f"¥{trade.amount:,.2f} | "
                    f"¥{trade.commission:.2f} |"
                )
            md.append("")

        # 页脚
        md.append("---")
        md.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        md.append("")
        md.append("*由 ClaudeQuant 自动生成*")
        md.append("")

        return '\n'.join(md)

    def _generate_charts(self, result: BacktestResult, file_prefix: str):
        """生成图表"""
        # 设置中文字体（避免中文乱码）
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 1. 资金曲线
        fig, ax = plt.subplots(figsize=(12, 6))
        result.portfolio_values.plot(ax=ax, linewidth=2, color='#2E86AB')
        ax.set_title(f'{result.symbol} - Portfolio Value', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value (¥)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=result.initial_capital, color='red', linestyle='--', alpha=0.5, label='Initial Capital')
        ax.legend()

        equity_path = self.output_dir / f"{result.symbol.replace('.', '_')}_equity.png"
        plt.tight_layout()
        plt.savefig(equity_path, dpi=100, bbox_inches='tight')
        plt.close()

        # 2. 回撤曲线
        cummax = result.portfolio_values.cummax()
        drawdown = (result.portfolio_values - cummax) / cummax

        fig, ax = plt.subplots(figsize=(12, 6))
        drawdown.plot(ax=ax, linewidth=2, color='#A23B72', kind='area', alpha=0.3)
        ax.set_title(f'{result.symbol} - Drawdown', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.1f}%'))
        ax.grid(True, alpha=0.3)

        dd_path = self.output_dir / f"{result.symbol.replace('.', '_')}_drawdown.png"
        plt.tight_layout()
        plt.savefig(dd_path, dpi=100, bbox_inches='tight')
        plt.close()

        logger.info(f"Charts generated: {equity_path}, {dd_path}")
