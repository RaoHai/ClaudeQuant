#!/bin/bash
# Quote skill - 获取实时行情

# Change to project root
cd "$(dirname "$0")/../../.." || exit 1

# Validate arguments
if [ -z "$1" ]; then
    echo "❌ 错误：缺少股票代码"
    echo ""
    echo "用法: /quote <股票代码>"
    echo ""
    echo "示例："
    echo "  /quote 600519    # 贵州茅台"
    echo "  /quote 000858    # 五粮液"
    echo "  /quote 601318    # 中国平安"
    echo ""
    echo "💡 提示：代码不需要带市场后缀（.SH/.SZ），系统会自动识别"
    exit 1
fi

# Execute quote command
python3 cli.py quote "$1"

# Return exit code
exit $?
