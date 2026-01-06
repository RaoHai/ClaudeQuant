#!/bin/bash
# Portfolio Skill - 查看持仓概况

cd "$(dirname "$0")/.." || exit 1

python3 cli.py portfolio
