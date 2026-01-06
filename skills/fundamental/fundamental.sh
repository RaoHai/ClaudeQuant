#!/bin/bash
# Fundamental skill - 基本面分析（资金面、机构持仓、政策面）

# Change to project root
cd "$(dirname "$0")/../.." || exit 1

# Check if symbol is provided
if [ -z "$1" ]; then
    echo "❌ 请提供股票代码"
    echo "用法: fundamental <股票代码>"
    echo "示例: fundamental 002202"
    exit 1
fi

symbol=$1

echo "🔄 正在分析 $symbol 的基本面..."
echo ""

# Execute fundamental analysis command
python3 cli.py fundamental "$symbol"

# Capture exit code
exit_code=$?

# Check if successful
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "💡 提示：结合技术面分析可获得更全面的判断"
    echo "   运行: python3 cli.py technical $symbol"
fi

# Return exit code
exit $exit_code
