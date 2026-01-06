#!/bin/bash
# Technical Skill - 技术分析

cd "$(dirname "$0")/.." || exit 1

if [ -z "$1" ]; then
    echo "用法: /technical <股票代码>"
    echo "示例: /technical 000001"
    exit 1
fi

python3 cli.py technical "$1"
