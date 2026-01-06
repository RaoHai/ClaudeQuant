# ClaudeQuant

A股量化交易平台 - 基于 Claude Code 的轻量级量化回测系统

## 特性

- **数据管理**: 支持 Tushare/AkShare 免费数据源，Parquet 格式高效存储
- **策略开发**: 简洁的策略开发框架，内置双均线等经典策略模板
- **回测引擎**: 事件驱动的回测引擎，支持手续费、滑点、印花税
- **性能分析**: 自动计算夏普比率、最大回撤、年化收益等指标
- **Markdown 报告**: 生成可读性强的回测报告，包含资金曲线图
- **CLI 交互**: 命令行界面，易于使用和自动化
- **无 UI 依赖**: 纯命令行 + Markdown，适合服务器环境

## 快速开始

### 1. 环境准备

**要求**:
- Python 3.9+
- pip 或 Poetry

**安装依赖**:

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 Poetry
poetry install
```

**配置环境变量**:

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Tushare Token
# 注册地址: https://tushare.pro/
TUSHARE_TOKEN=your_token_here
```

### 2. 下载数据

```bash
# 下载平安银行 (000001.SZ) 2023年全年数据
python -m src.cli.main data download --symbol 000001 --start 20230101 --end 20231231
```

### 3. 运行回测

```bash
# 运行双均线策略回测
python -m src.cli.main backtest \
  --strategy ma_cross \
  --symbol 000001 \
  --start 20230101 \
  --end 20231231
```

### 4. 查看报告

回测完成后，报告将保存在 `reports/backtest/` 目录下：

```bash
# 查看最新报告
cat reports/backtest/latest.md
```

## 项目结构

```
ClaudeQuant/
├── config/                  # 配置文件
├── data/                    # 数据存储（Parquet + SQLite）
├── reports/                 # Markdown 报告
├── strategies/              # 策略库
│   ├── templates/          # 策略模板
│   └── custom/             # 用户自定义策略
├── src/                     # 源代码
│   ├── cli/                # CLI 命令
│   ├── core/               # 核心类型和常量
│   ├── data/               # 数据模块
│   ├── strategy/           # 策略框架
│   ├── backtest/           # 回测引擎
│   └── utils/              # 工具函数
└── README.md
```

## 使用指南

### 数据管理

```bash
# 下载数据
python -m src.cli.main data download -s 000001 --start 20230101 --end 20231231

# 更新数据（增量）
python -m src.cli.main data update -s 000001 --days 30

# 查看数据信息
python -m src.cli.main data info -s 000001

# 列出所有已缓存的股票
python -m src.cli.main data info

# 清除缓存
python -m src.cli.main data clear -s 000001 --confirm
```

### 策略回测

```bash
# 基础回测
python -m src.cli.main backtest \
  --strategy ma_cross \
  --symbol 000001 \
  --start 20230101 \
  --end 20231231

# 自定义策略参数
python -m src.cli.main backtest \
  --strategy ma_cross \
  --symbol 000001 \
  --start 20230101 \
  --end 20231231 \
  --params "fast_period=10,slow_period=30"

# 指定初始资金
python -m src.cli.main backtest \
  --strategy ma_cross \
  --symbol 000001 \
  --start 20230101 \
  --end 20231231 \
  --capital 200000
```

## 开发自定义策略

### 策略模板

创建文件 `strategies/custom/my_strategy.py`:

```python
from src.strategy.base import Strategy
from src.strategy.indicators import calculate_ma
from src.core.types import Signal, SignalAction
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self, params=None):
        default_params = {
            'period': 20,
        }
        if params:
            default_params.update(params)
        super().__init__(default_params)
        self.period = self.params['period']

    def init(self, data: pd.DataFrame):
        """初始化 - 计算指标"""
        self.data = data.copy()
        self.data['ma'] = calculate_ma(self.data['close'], self.period)

    def next(self, bar: pd.Series):
        """生成信号"""
        # 你的策略逻辑
        if bar['close'] > bar['ma'] and self.current_position == 0:
            return self.create_signal(
                action=SignalAction.BUY,
                price=bar['close'],
                quantity=100,
                reason="Price above MA"
            )

        elif bar['close'] < bar['ma'] and self.current_position > 0:
            return self.create_signal(
                action=SignalAction.SELL,
                price=bar['close'],
                quantity=self.current_position,
                reason="Price below MA"
            )

        return None
```

## 配置说明

### config/default.yaml

```yaml
system:
  data_dir: ./data
  report_dir: ./reports
  log_level: INFO

backtest:
  initial_capital: 100000.0
  commission:
    stock: 0.0003  # 万三手续费
    min_commission: 5.0
  slippage: 0.0001

risk:
  max_position_size: 0.2  # 单仓位最大20%
  max_positions: 10
```

## 回测报告示例

回测报告包含以下内容：

1. **基本信息**: 策略名称、股票代码、回测区间、初始/最终资金
2. **收益统计**: 总收益率、年化收益率、最大回撤、夏普比率等
3. **交易统计**: 交易次数、手续费、交易天数
4. **资金曲线**: 可视化资产变化
5. **回撤曲线**: 可视化回撤情况
6. **交易明细**: 每笔交易的详细记录

## 性能指标说明

| 指标 | 说明 |
|------|------|
| 总收益率 | 期间总收益百分比 |
| 年化收益率 | 按年计算的收益率 |
| 最大回撤 | 资产最大跌幅 |
| 夏普比率 | 风险调整后收益（>1 较好，>2 优秀）|
| 索提诺比率 | 只考虑下行风险的夏普比率 |
| 卡玛比率 | 年化收益率 / 最大回撤 |

## 常见问题

### 1. Tushare Token 在哪里获取？

访问 https://tushare.pro/ 注册账号，在个人中心获取 Token。

### 2. 如何添加新的数据源（如 AkShare）？

在 `src/data/providers/` 目录下创建新的提供者类，继承 `DataProvider` 基类。

### 3. 如何扩展回测指标？

编辑 `src/backtest/metrics.py`，在 `MetricsCalculator` 类中添加新的指标计算方法。

### 4. 回测结果不准确？

检查以下设置：
- 手续费率是否符合实际（默认万三）
- 滑点设置是否合理
- 数据是否完整（周末和节假日无交易）

## 路线图

- [x] 数据下载和缓存
- [x] 双均线策略示例
- [x] 回测引擎
- [x] Markdown 报告生成
- [ ] MACD、RSI 等更多策略模板
- [ ] Claude Skills 集成
- [ ] 模拟交易账户
- [ ] 多股票组合回测
- [ ] 参数优化

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- [Tushare](https://tushare.pro/) - 提供 A股数据
- [Claude Code](https://claude.com/claude-code) - AI 驱动的开发工具
- 所有开源库的作者

---

**ClaudeQuant** - 让量化交易更简单

Generated with [Claude Code](https://claude.com/claude-code)
