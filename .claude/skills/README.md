# ClaudeQuant Skills

Claude Code Skills 集合，用于股票持仓分析和技术指标计算。

## 目录结构

```
skills/
├── portfolio/          # 持仓概况 skill
│   ├── SKILL.md       # Skill 元数据和文档
│   └── portfolio.sh   # 执行脚本
├── quote/             # 实时行情 skill
│   ├── SKILL.md
│   └── quote.sh
├── technical/         # 技术分析 skill
│   ├── SKILL.md
│   └── technical.sh
└── analyze/           # 分析报告 skill
    ├── SKILL.md
    └── analyze.sh
```

## 可用 Skills

### 📊 `/portfolio` - 查看持仓概况

显示所有持仓股票的实时行情和涨跌幅。

**详细文档**：[skills/portfolio/SKILL.md](portfolio/SKILL.md)

### 📈 `/quote <代码>` - 获取实时行情

获取指定股票的详细行情数据。

**详细文档**：[skills/quote/SKILL.md](quote/SKILL.md)

### 📊 `/technical <代码>` - 技术分析

对指定股票进行技术指标分析（MA/MACD/RSI/布林带）。

**详细文档**：[skills/technical/SKILL.md](technical/SKILL.md)

### 📝 `/analyze` - 生成完整分析报告

生成所有持仓股票的完整分析报告（Markdown格式）。

**详细文档**：[skills/analyze/SKILL.md](analyze/SKILL.md)

## 快速使用

### 在 Claude Code 对话中

直接用自然语言提问，Claude 会自动调用相应的 skill：

```
你：我的持仓现在怎么样？
Claude：[自动调用 /portfolio]

你：帮我看看贵州茅台的行情
Claude：[自动调用 /quote 600519]

你：分析一下贵州茅台的技术面
Claude：[自动调用 /technical 600519]

你：生成一份完整的分析报告
Claude：[自动调用 /analyze]
```

### 直接执行

也可以在命令行直接运行：

```bash
./skills/portfolio/portfolio.sh
./skills/quote/quote.sh 600519
./skills/technical/technical.sh 600519
./skills/analyze/analyze.sh
```

## Skill 结构说明

每个 skill 包含两个文件：

### 1. SKILL.md - 元数据文档

包含以下内容：
- **Description** - 功能描述
- **Arguments** - 参数说明
- **Dependencies** - 依赖项
- **Configuration** - 配置要求
- **Examples** - 使用示例
- **Output** - 输出格式
- **Natural Language Triggers** - 自然语言触发方式
- **Exit Codes** - 退出码说明
- **Notes** - 注意事项

### 2. [skillname].sh - 执行脚本

Shell 脚本特点：
- 以 `#!/bin/bash` 开头
- 导航到项目根目录
- 参数验证
- 调用 Python CLI 工具
- 返回正确的退出码

## 开发新 Skill

### 步骤

1. **创建目录**
   ```bash
   mkdir skills/myskill
   ```

2. **创建 SKILL.md**
   ```bash
   cat > skills/myskill/SKILL.md << 'EOF'
   # MySkill

   简短描述

   ## Description
   详细说明...
   EOF
   ```

3. **创建执行脚本**
   ```bash
   cat > skills/myskill/myskill.sh << 'EOF'
   #!/bin/bash
   cd "$(dirname "$0")/../.." || exit 1
   python3 cli.py mycommand "$@"
   exit $?
   EOF
   ```

4. **设置可执行权限**
   ```bash
   chmod +x skills/myskill/myskill.sh
   ```

5. **测试 Skill**
   ```bash
   ./skills/myskill/myskill.sh
   ```

### Skill 模板

参考 [skills/portfolio](portfolio) 作为模板。

## 依赖

所有 skills 依赖于：

- Python 3.9+
- pandas
- numpy
- akshare
- python-dotenv

安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

在 `.env` 文件中配置：

```env
PORTFOLIO_SYMBOLS=600519,000858,601318
LOG_LEVEL=INFO
```

## 故障排查

### Skill 无法执行

检查权限：
```bash
chmod +x skills/*/*.sh
```

### 找不到模块

检查是否在项目根目录：
```bash
cd "$(dirname "$0")/../.."
pwd  # 应该是项目根目录
```

### 参数错误

查看 SKILL.md 了解正确的参数格式。

## 更多信息

- **项目文档**：[CLAUDE.md](../CLAUDE.md)
- **快速开始**：[.claude/QUICKSTART.md](../.claude/QUICKSTART.md)
- **Claude Code 文档**：https://code.claude.com/docs/en/skills

---

**让 AI 成为你的投资助手！** 🚀
