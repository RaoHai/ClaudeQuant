#!/bin/bash
# Quote Skill - 获取实时行情

cd "$(dirname "$0")/.." || exit 1

if [ -z "$1" ]; then
    echo "用法: /quote <股票代码>"
    echo "示例: /quote 000001"
    exit 1
fi

python3 cli.py quote "$1"
