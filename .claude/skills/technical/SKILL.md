# Technical

技术分析 - 对指定股票进行全面的技术指标分析

## Description

对指定股票进行技术指标分析，包括均线系统、MACD、RSI、布林带等指标，并基于多个指标给出综合买卖建议。

## Arguments

- `<stock_code>` - 股票代码（必需）
  - 格式：不需要带市场后缀（.SH/.SZ）
  - 示例：`600519`（贵州茅台）、`000858`（五粮液）、`601318`（中国平安）

## Dependencies

- Python 3.9+
- pandas
- numpy
- akshare
- python-dotenv

## Configuration

```env
```

技术指标参数可在 `config/default.yaml` 中配置：
```yaml
analysis:
  indicators:
    ma:
      periods: [5, 10, 20, 60]
    rsi:
      period: 14
      overbought: 70
      oversold: 30
```

## Technical Indicators

### 均线系统 (MA)
- MA5/MA10：短期趋势
- MA20：中期趋势
- MA60：长期趋势
- 金叉/死叉检测

### MACD
- 快慢线交叉
- 柱状图多空判断

### RSI（相对强弱指标）
- 14日RSI
- 超买/超卖判断（>70 超买，<30 超卖）

### 布林带 (Bollinger Bands)
- 上下轨突破检测

### 综合信号
- 🟢 买入信号
- 🔴 卖出信号
- 🟡 持有观望

## Examples

```bash
/technical 600519
/technical 000858
/technical 601318
```

## Output

```
📊 技术分析: 600519.SH

当前价格: ¥1650.00
涨跌幅: +2.50%

均线系统:
  MA5: ¥1638.50 ↑
  MA10: ¥1625.80 ↑
  MA20: ¥1610.20 ↑
  🟢 金叉

RSI(14): 65.23 - 🟡 正常

综合信号: 🟢 买入信号
```

## Natural Language Triggers

Claude 会在以下情况自动调用此 skill：

- "分析600519的技术面"
- "贵州茅台的技术指标怎么样"
- "帮我看看贵州茅台的技术分析"
- "600519现在是买入还是卖出信号"
- "技术面分析一下贵州茅台"

## Exit Codes

- `0` - 成功完成技术分析
- `1` - 缺少股票代码参数或分析失败

## Error Messages

如果缺少参数，会显示：
```
❌ 错误：缺少股票代码

用法: /technical <股票代码>

示例：
  /technical 600519    # 分析贵州茅台
  /technical 000858    # 分析五粮液
  /technical 601318    # 分析中国平安

💡 提示：代码不需要带市场后缀（.SH/.SZ），系统会自动识别

技术指标包括：
  • 均线系统（MA5/10/20/60）
  • MACD 指标
  • RSI 相对强弱指标
  • 布林带
  • 综合买卖信号
```

## Notes

- 分析基于最近60个交易日的数据
- 技术指标仅供参考，不构成投资建议
- 系统会自动识别股票市场并添加后缀
- 综合信号基于多个指标加权计算
