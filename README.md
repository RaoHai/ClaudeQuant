# ClaudeQuant - AI 持仓分析助手

基于 Claude Code 的 A股持仓智能分析助手。通过 Claude 的 AI 能力，自动分析你的股票持仓，提供技术面分析、行情追踪和操作建议。

## 核心特性

- 🤖 **AI 驱动**: 利用 Claude 的智能分析能力
- 📊 **实时行情**: 获取最新股票行情（15分钟延迟）
- 📈 **技术分析**: 自动计算 MA、MACD、RSI、布林带等指标
- 💡 **智能建议**: 基于技术指标给出买入/卖出/持有建议
- 📝 **Markdown 报告**: 生成易读的分析报告
- ⚡ **Skills 集成**: 通过 Claude Code Skills 对话式交互

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置持仓

编辑 `.env` 文件（从 `.env.example` 复制）：

```bash
cp .env.example .env
```

配置你的持仓代码：

```env
# Tushare Token (注册: https://tushare.pro/)
TUSHARE_TOKEN=your_token_here

# 持仓股票代码（逗号分隔）
PORTFOLIO_SYMBOLS=600519,000858,601318
```

### 3. 使用 Claude Code Skills

在 Claude Code 中，你可以这样问：

**"当前持仓的状况是怎样的？"**

Claude 会自动调用 Skills 获取数据并分析。

## Skills 命令

### `/portfolio` - 查看持仓概况

```bash
./skills/portfolio.sh
```

显示所有持仓股票的实时行情和涨跌幅。

### `/quote <代码>` - 获取实时行情

```bash
./skills/quote.sh 600519
```

获取指定股票的详细行情数据。

### `/technical <代码>` - 技术分析

```bash
./skills/technical.sh 600519
```

对指定股票进行技术指标分析，包括：
- 均线系统 (MA5/10/20/60)
- MACD 指标
- RSI 指标
- 综合买卖信号

### `/analyze` - 完整分析报告

```bash
./skills/analyze.sh
```

生成所有持仓股票的完整分析报告，保存为 Markdown 文件。

## 使用场景

### 场景 1: 每日盘后分析

在 Claude Code 中问：

> "帮我分析一下今天持仓的表现，有哪些需要关注的？"

Claude 会：
1. 调用 `/analyze` 生成报告
2. 阅读报告内容
3. 用自然语言总结关键信息
4. 提供个性化建议

### 场景 2: 单只股票深度分析

在 Claude Code 中问：

> "平安银行(600519)现在的技术面如何？"

Claude 会：
1. 调用 `/quote 600519` 获取实时行情
2. 调用 `/technical 600519` 进行技术分析
3. 分析各项指标的含义
4. 给出操作建议

### 场景 3: 市场情绪判断

在 Claude Code 中问：

> "我的持仓整体风险如何？需要调整吗？"

Claude 会：
1. 调用 `/portfolio` 查看概况
2. 逐个分析技术指标
3. 评估整体仓位风险
4. 提供调仓建议

## 技术指标说明

### 均线 (MA)
- **MA5/MA10**: 短期趋势
- **MA20**: 中期趋势
- **MA60**: 长期趋势
- **金叉**: MA5 上穿 MA20，看涨信号
- **死叉**: MA5 下穿 MA20，看跌信号

### MACD
- **多头**: histogram > 0，上涨趋势
- **空头**: histogram < 0，下跌趋势
- **金叉**: MACD 线上穿信号线
- **死叉**: MACD 线下穿信号线

### RSI (相对强弱指标)
- **超买**: RSI > 70，可能回调
- **超卖**: RSI < 30，可能反弹
- **正常**: 30 < RSI < 70

### 布林带 (Bollinger Bands)
- **突破上轨**: 超买，可能回调
- **突破下轨**: 超卖，可能反弹
- **在轨道内**: 正常波动范围

## 项目结构

```
ClaudeQuant/
├── .env                    # 持仓配置
├── cli.py                  # CLI 工具
├── config/
│   └── default.yaml        # 系统配置
├── skills/                 # Claude Code Skills
│   ├── portfolio.sh        # 持仓概况
│   ├── quote.sh            # 实时行情
│   ├── technical.sh        # 技术分析
│   └── analyze.sh          # 完整分析
├── src/
│   ├── quote/              # 行情获取
│   ├── analysis/           # 技术分析
│   ├── report/             # 报告生成
│   └── utils/              # 工具函数
└── reports/                # 分析报告输出
```

## 配置说明

### config/default.yaml

```yaml
# 技术分析配置
analysis:
  indicators:
    ma:
      periods: [5, 10, 20, 60]  # 均线周期
    rsi:
      period: 14
      overbought: 70  # 超买线
      oversold: 30    # 超卖线

# 报告配置
report:
  history_days: 60  # 分析最近60天数据
```

## 与 Claude 对话示例

**你**: 当前持仓的状况是怎样的？

**Claude**:
让我帮你查看持仓状况。

*[调用 /portfolio skill]*

根据最新数据，你持有的3只股票今日表现如下：
- 贵州茅台(600519.SH): 1650.00元，涨2.5%
- 五粮液(000858.SZ): 158.60元，涨1.8%
- 中国平安(601318.SH): 45.20元，跌0.5%

需要我进一步分析技术面吗？

---

**你**: 帮我看看贵州茅台的技术指标

**Claude**:
*[调用 /technical 600519]*

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

本工具仅供参考，不构成投资建议。股市有风险，投资需谨慎。

## 许可证

MIT License

---

**ClaudeQuant** - 让 AI 成为你的投资助手

Generated with [Claude Code](https://claude.com/claude-code)
