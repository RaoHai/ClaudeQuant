#!/bin/bash
# Portfolio skill - 查看持仓概况

# Change to project root
cd "$(dirname "$0")/../../.." || exit 1

# Execute portfolio command
python3 cli.py portfolio

# Return exit code
exit $?
