"""ClaudeQuant 常量定义"""

# 市场常量
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "15:00"
MARKET_MORNING_CLOSE = "11:30"
MARKET_AFTERNOON_OPEN = "13:00"

# 交易常量
STOCK_LOT_SIZE = 100  # A股一手 = 100股
MIN_PRICE_TICK = 0.01  # 最小价格变动单位

# 默认手续费和滑点
DEFAULT_COMMISSION_RATE = 0.0003  # 万三
DEFAULT_MIN_COMMISSION = 5.0  # 最低5元
DEFAULT_SLIPPAGE = 0.0001  # 万一滑点
DEFAULT_STAMP_TAX = 0.001  # 印花税 (卖出时收取)

# 数据列名标准化
OHLCV_COLUMNS = {
    'ts_code': 'symbol',
    'trade_date': 'date',
    'open': 'open',
    'high': 'high',
    'low': 'low',
    'close': 'close',
    'pre_close': 'pre_close',
    'change': 'change',
    'pct_chg': 'pct_change',
    'vol': 'volume',  # 手
    'amount': 'amount',  # 千元
}

# 标准列名
STD_COLUMNS = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']

# 性能指标常量
TRADING_DAYS_PER_YEAR = 252  # 一年交易日数量
RISK_FREE_RATE = 0.03  # 默认无风险利率

# 文件路径
DATA_DIR = './data'
REPORT_DIR = './reports'
LOG_DIR = './logs'
CONFIG_DIR = './config'

# 数据格式
DATE_FORMAT = '%Y%m%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
REPORT_DATE_FORMAT = '%Y-%m-%d'

# 市场代码
MARKET_SH = 'SH'  # 上海证券交易所
MARKET_SZ = 'SZ'  # 深圳证券交易所
MARKET_BJ = 'BJ'  # 北京证券交易所
