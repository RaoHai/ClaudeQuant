#!/usr/bin/env python3
"""测试行情获取"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.quote.provider import QuoteProvider

    print("初始化 QuoteProvider...")
    provider = QuoteProvider()

    print("获取 002202 行情...")
    quote = provider.get_realtime_quote('002202')

    print("\n✅ 成功获取行情:")
    print(f"代码: {quote['symbol']}")
    print(f"名称: {quote['name']}")
    print(f"最新价: ¥{quote['close']:.2f}")
    print(f"涨跌幅: {quote['pct_change']:+.2f}%")
    print(f"成交量: {quote['volume'] / 100:,.0f} 手")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
