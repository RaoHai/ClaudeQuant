#!/bin/bash
# Deep Analysis skill - 深度分析（概念板块、对外投资、隐藏关联）

# Change to project root
cd "$(dirname "$0")/../../.." || exit 1

# Check if symbol is provided
if [ -z "$1" ]; then
    echo "❌ 请提供股票代码"
    echo "用法: deep <股票代码>"
    echo "示例: deep 002202"
    exit 1
fi

symbol=$1

echo "🔍 正在深度挖掘 $symbol 的隐藏信息..."
echo ""

# Execute deep analysis command
python3 cli.py deep "$symbol"

# Capture exit code
exit_code=$?

# Check if successful
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "💡 提示：结合基本面和技术面可获得完整投资逻辑"
fi

# Return exit code
exit $exit_code
