#!/bin/bash
# Analyze skill - 生成完整分析报告

# Change to project root
cd "$(dirname "$0")/../.." || exit 1

echo "🔄 正在生成持仓分析报告..."
echo ""

# Execute analyze command
python3 cli.py analyze

# Capture exit code
exit_code=$?

# Check if successful
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✨ 提示：你可以让我帮你解读报告内容"
fi

# Return exit code
exit $exit_code
