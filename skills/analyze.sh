#!/bin/bash
# Analyze Skill - 生成完整分析报告

cd "$(dirname "$0")/.." || exit 1

python3 cli.py analyze
