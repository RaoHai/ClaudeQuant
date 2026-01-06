#!/bin/bash
# Technical skill - 技术分析

# Change to project root
cd "$(dirname "$0")/../../.." || exit 1

# Validate arguments
if [ -z "$1" ]; then
    echo "❌ 错误：缺少股票代码"
    echo ""
    echo "用法: /technical <股票代码>"
    echo ""
    echo "示例："
    echo "  /technical 600519    # 分析贵州茅台"
    echo "  /technical 000858    # 分析五粮液"
    echo "  /technical 601318    # 分析中国平安"
    echo ""
    echo "💡 提示：代码不需要带市场后缀（.SH/.SZ），系统会自动识别"
    echo ""
    echo "技术指标包括："
    echo "  • 均线系统（MA5/10/20/60）"
    echo "  • MACD 指标"
    echo "  • RSI 相对强弱指标"
    echo "  • 布林带"
    echo "  • 综合买卖信号"
    exit 1
fi

# Execute technical analysis command
python3 cli.py technical "$1"

# Return exit code
exit $?
