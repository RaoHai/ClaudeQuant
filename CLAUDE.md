# ClaudeQuant - AI 持仓分析助手

基于 Claude Code 的 A股持仓智能分析助手。通过 Claude 的 AI 能力，自动分析你的股票持仓，提供技术面分析、行情追踪和操作建议。

## 项目概述

这是一个对话式的股票分析工具，通过 Claude Code Skills 集成，让你可以用自然语言与 AI 交互来分析股票持仓。

**核心特性**：
- 🤖 **AI 驱动**: 利用 Claude 的智能分析能力
- 📊 **实时行情**: 获取最新股票行情
- 📈 **技术分析**: 自动计算 MA、MACD、RSI、布林带等指标
- 💡 **智能建议**: 基于技术指标给出买入/卖出/持有建议
- 📝 **Markdown 报告**: 生成易读的分析报告

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：
- `pandas>=2.0.0` - 数据处理
- `akshare>=1.12.0` - 行情数据源（免费，无需 Token）
- `click>=8.1.0` - CLI 工具
- `python-dotenv>=1.0.0` - 环境变量管理

### 2. 配置持仓

复制并编辑 `.env` 文件：

```bash
cp .env.example .env
```

配置内容：
```env
# 持仓股票代码（逗号分隔，不带市场后缀）
PORTFOLIO_SYMBOLS=600519,000858,601318

# 日志级别（可选）
LOG_LEVEL=INFO
```

**重要提示**：
- 股票代码格式：深圳 `000001`、上海 `600519`、北交所 `430090`
- 系统会自动识别市场并添加后缀（.SZ/.SH/.BJ）
- 数据源使用 AkShare，完全免费，无需注册或 Token

### 3. 使用 Claude Code Skills

在 Claude Code 对话中，你可以这样问：

**查看持仓概况**：
```
"当前持仓的状况是怎样的？"
```

**分析单只股票**：
```
"帮我分析一下贵州茅台(600519)的技术面"
```

**生成完整报告**：
```
"给我生成一份完整的持仓分析报告"
```

Claude 会自动调用相应的 Skills 获取数据并提供智能分析。

## 项目结构

```
ClaudeQuant/
├── .claude/              # Claude Code 配置
│   ├── QUICKSTART.md     # 快速开始指南
│   └── settings.local.json
├── .env                  # 持仓配置（需手动创建）
├── cli.py                # CLI 工具入口
├── config/
│   └── default.yaml      # 技术分析配置
├── skills/               # Claude Code Skills
│   ├── portfolio.sh      # 持仓概况
│   ├── quote.sh          # 实时行情
│   ├── technical.sh      # 技术分析
│   └── analyze.sh        # 完整分析
├── src/
│   ├── quote/            # 行情获取模块
│   │   └── provider.py   # QuoteProvider - 行情数据接口
│   ├── analysis/         # 技术分析模块
│   │   ├── analyzer.py   # TechnicalAnalyzer - 技术指标计算
│   │   └── technical.py  # 指标计算函数
│   ├── report/           # 报告生成模块
│   │   └── generator.py  # ReportGenerator - Markdown报告
│   ├── core/             # 核心类型和异常
│   └── utils/            # 工具函数
└── reports/              # 分析报告输出目录
```

## 核心模块说明

### 1. QuoteProvider (src/quote/provider.py)

行情数据提供者，负责从 AkShare 获取股票数据。

**主要方法**：
- `get_realtime_quote(symbol)` - 获取实时行情
- `get_historical_data(symbol, days)` - 获取历史K线数据
- `get_portfolio_quotes(symbols)` - 批量获取持仓行情

**数据源**：
- 使用 AkShare 接口，数据来自东方财富
- 完全免费，无需注册或 Token
- 无频率限制

**使用示例**：
```python
from src.quote.provider import QuoteProvider

provider = QuoteProvider()
quote = provider.get_realtime_quote('600519')
# 返回: {symbol, name, close, pct_change, ...}
```

### 2. TechnicalAnalyzer (src/analysis/analyzer.py)

技术指标分析器，计算各类技术指标并生成买卖信号。

**支持的指标**：
- **MA (移动平均线)**: MA5/10/20/60，金叉/死叉检测
- **MACD**: 快慢线、柱状图，多空趋势判断
- **RSI (相对强弱指标)**: 14日RSI，超买/超卖判断
- **布林带**: 上下轨，突破检测

**使用示例**：
```python
from src.analysis.analyzer import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()
data = provider.get_historical_data('600519', days=60)
analysis = analyzer.analyze(data)
# 返回: {signal, ma, macd, rsi, bollinger, ...}
```

### 3. ReportGenerator (src/report/generator.py)

报告生成器，将分析结果格式化为 Markdown 报告。

**主要方法**：
- `generate_portfolio_report(quotes, analyses)` - 生成持仓分析报告

**输出位置**：
- `reports/portfolio_YYYYMMDD_HHMMSS.md` - 带时间戳的报告
- `reports/latest.md` - 最新报告的软链接

## CLI 命令

虽然主要通过 Claude Code 对话使用，但也可以直接运行 CLI 命令：

```bash
# 查看持仓概况
python cli.py portfolio

# 获取实时行情
python cli.py quote 600519

# 技术分析
python cli.py technical 600519

# 生成完整分析报告
python cli.py analyze
```

## Skills 说明

### /portfolio - 持仓概况

显示所有持仓股票的实时行情和涨跌幅。

**触发方式**：
- "查看持仓"
- "我的股票现在怎么样"
- "持仓概况"

**输出示例**：
```
📊 持仓概况

代码         名称      最新价    涨跌幅
----------------------------------------
600519.SH   贵州茅台  1650.00   +2.50%
000858.SZ   五粮液     158.60   +1.80%
601318.SH   中国平安    45.20   -0.50%
```

### /quote <代码> - 实时行情

获取指定股票的详细行情数据。

**触发方式**：
- "查看600519的行情"
- "贵州茅台现在多少钱"

**输出示例**：
```
📈 贵州茅台 (600519.SH)

最新价: ¥1650.00
涨跌幅: +2.50%
涨跌额: +40.30
开盘价: ¥1620.00
...
```

### /technical <代码> - 技术分析

对指定股票进行技术指标分析。

**触发方式**：
- "分析600519的技术面"
- "贵州茅台的技术指标怎么样"

**输出示例**：
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

### /analyze - 完整分析报告

生成所有持仓股票的完整分析报告。

**触发方式**：
- "生成分析报告"
- "帮我做个完整的持仓分析"

**输出**：生成 Markdown 报告文件并返回路径

## 技术指标说明

### 均线 (MA)

- **MA5/MA10**: 短期趋势，灵敏度高
- **MA20**: 中期趋势，月线
- **MA60**: 长期趋势，季线
- **金叉**: MA5上穿MA20，看涨信号
- **死叉**: MA5下穿MA20，看跌信号

### MACD

- **DIF**: 快线，12日EMA - 26日EMA
- **DEA**: 慢线，DIF的9日EMA
- **Histogram**: 柱状图，DIF - DEA
- **金叉**: DIF上穿DEA，买入信号
- **死叉**: DIF下穿DEA，卖出信号

### RSI (相对强弱指标)

- **计算**: 14日相对强弱
- **超买**: RSI > 70，可能回调
- **超卖**: RSI < 30，可能反弹
- **正常**: 30 < RSI < 70

### 布林带 (Bollinger Bands)

- **中轨**: 20日均线
- **上轨**: 中轨 + 2倍标准差
- **下轨**: 中轨 - 2倍标准差
- **突破上轨**: 超买区域
- **突破下轨**: 超卖区域

## 配置说明

### config/default.yaml

```yaml
analysis:
  indicators:
    ma:
      periods: [5, 10, 20, 60]  # 均线周期
    macd:
      fast_period: 12
      slow_period: 26
      signal_period: 9
    rsi:
      period: 14
      overbought: 70  # 超买线
      oversold: 30    # 超卖线
    bollinger:
      period: 20
      std_dev: 2

report:
  history_days: 60  # 分析最近60天数据
  output_dir: reports
```

## 常见问题

### Q: 如何添加或修改持仓？

A: 编辑 `.env` 文件中的 `PORTFOLIO_SYMBOLS`：
```env
PORTFOLIO_SYMBOLS=600519,000858,601318,000333
```

### Q: 数据源准确吗？

A: 项目使用 AkShare 数据源，来自东方财富网，数据质量可靠。实时行情和资金流向数据都是免费且准确的。

### Q: 技术指标可以自定义吗？

A: 可以。编辑 `config/default.yaml` 修改指标参数。

### Q: 报告保存在哪里？

A: `reports/` 目录下，文件名包含时间戳。`reports/latest.md` 指向最新报告。

### Q: 支持港股、美股吗？

A: 当前仅支持 A股（沪深北）。后续版本可能增加港股美股支持。

## 开发指南

### 添加新的技术指标

1. 在 `src/analysis/technical.py` 添加指标计算函数
2. 在 `TechnicalAnalyzer.analyze()` 中调用
3. 更新 `config/default.yaml` 添加配置
4. 在报告模板中展示新指标

### 添加新的 Skill

1. 在 `cli.py` 添加新命令
2. 在 `skills/` 创建 `.sh` 脚本
3. 更新文档说明使用方式

## 与 Claude 对话示例

**你**: 当前持仓的状况是怎样的？

**Claude**: 让我帮你查看持仓状况。
*[调用 /portfolio skill]*

根据最新数据，你持有的3只股票今日表现如下：
- 贵州茅台(600519.SH): 1650.00元，涨2.5%
- 五粮液(000858.SZ): 158.60元，涨1.8%
- 中国平安(601318.SH): 45.20元，跌0.5%

需要我进一步分析技术面吗？

---

**你**: 帮我看看贵州茅台的技术指标

**Claude**: *[调用 /technical 600519]*

贵州茅台(600519)当前技术面分析：

均线系统：
- 当前价格在 MA5/MA10/MA20 上方，多头排列
- 短中长期趋势均向上
- 近期出现金叉，是买入信号

MACD：多头趋势，histogram 为正

RSI：65，处于正常区间，偏强势

综合信号：🟢 **买入信号**

建议：多个指标显示强势买入信号，茅台基本面优秀，可考虑逢低加仓，建议分批买入控制风险。

## 免责声明

本工具仅供参考，不构成投资建议。股市有风险，投资需谨谨。所有投资决策请基于自己的判断和风险承受能力。

## 许可证

MIT License

---

**让 AI 成为你的投资助手！**
