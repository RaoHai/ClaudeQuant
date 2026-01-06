# Analyze

生成完整分析报告 - 为所有持仓股票生成详细的技术分析报告

## Description

生成包含所有持仓股票的完整技术分析报告，以 Markdown 格式保存。报告包括持仓概况、每只股票的详细技术分析、操作建议等内容。

## Arguments

无需参数

## Dependencies

- Python 3.9+
- pandas
- numpy
- tushare
- python-dotenv

## Configuration

需要在 `.env` 文件中配置：
```env
TUSHARE_TOKEN=your_token_here
PORTFOLIO_SYMBOLS=600519,000858,601318
```

## Report Contents

生成的报告包含以下内容：

1. **持仓概况总览**
   - 所有股票的实时行情
   - 涨跌幅统计

2. **个股详细分析**
   - 基本信息（代码、名称、价格）
   - 技术指标（MA/MACD/RSI/布林带）
   - 综合买卖信号

3. **操作建议**
   - 基于技术面的操作建议
   - 风险提示

## Output Location

- **带时间戳的报告**：`reports/portfolio_YYYYMMDD_HHMMSS.md`
- **最新报告软链接**：`reports/latest.md`

## Examples

```bash
/analyze
```

## Output

```
🔄 正在生成持仓分析报告...

🔄 正在分析持仓...

  分析 600519.SH...
  分析 000858.SZ...
  分析 601318.SH...

📝 生成报告...

✅ 报告已生成: reports/portfolio_20260106_135500.md
   查看报告: cat reports/portfolio_20260106_135500.md

✨ 提示：你可以让我帮你解读报告内容
```

## Natural Language Triggers

Claude 会在以下情况自动调用此 skill：

- "生成分析报告"
- "帮我做个完整的持仓分析"
- "给我生成一份持仓分析报告"
- "分析一下我的所有持仓"
- "整体分析我的股票"

## Exit Codes

- `0` - 成功生成报告
- `1` - 配置错误或报告生成失败

## Report Format

报告以 Markdown 格式生成，包含：

```markdown
# 持仓分析报告

生成时间: 2026-01-06 13:55:00

## 持仓概况

| 代码 | 名称 | 最新价 | 涨跌幅 |
|------|------|--------|--------|
| 600519.SH | 贵州茅台 | 1650.00 | +2.50% |

## 个股分析

### 贵州茅台 (600519.SH)

**基本信息**
- 最新价：1650.00
- 涨跌幅：+2.50%

**技术指标**
- 均线：金叉
- RSI：65（正常）
- MACD：多头

**综合信号**：🟢 买入

**操作建议**：...
```

## Notes

- 报告生成需要几秒钟，请耐心等待
- 建议在收盘后生成报告，数据更完整
- 可以让 Claude 帮你解读报告内容
- 报告仅供参考，不构成投资建议

## Follow-up Actions

生成报告后，你可以：
1. 让 Claude 阅读并解释报告内容
2. 询问特定股票的详细分析
3. 请求操作建议
4. 对比历史报告
