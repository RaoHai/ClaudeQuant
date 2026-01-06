"""技术分析器"""

import pandas as pd
from typing import Dict, Any

from src.analysis.technical import (
    calculate_ma,
    calculate_macd,
    calculate_rsi,
    calculate_bollinger_bands,
)
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TechnicalAnalyzer:
    """技术指标分析器"""

    def __init__(self):
        """初始化"""
        self.config = get_config()

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        技术分析

        Args:
            data: 历史数据 DataFrame

        Returns:
            分析结果字典
        """
        if data.empty or len(data) < 20:
            return {'error': 'Insufficient data for analysis'}

        result = {}

        # 当前价格
        current = data.iloc[-1]
        result['current_price'] = float(current['close'])
        result['pct_change'] = float(current.get('pct_change', 0))

        # 均线分析
        result['ma'] = self._analyze_ma(data)

        # MACD 分析
        result['macd'] = self._analyze_macd(data)

        # RSI 分析
        result['rsi'] = self._analyze_rsi(data)

        # 布林带分析
        result['bollinger'] = self._analyze_bollinger(data)

        # 综合信号
        result['signal'] = self._generate_signal(result)

        logger.info(f"Technical analysis completed: signal={result['signal']}")

        return result

    def _analyze_ma(self, data: pd.DataFrame) -> Dict:
        """均线分析"""
        periods = self.config.get('analysis.indicators.ma.periods', [5, 10, 20, 60])

        ma_data = {}
        current_price = data.iloc[-1]['close']

        for period in periods:
            if len(data) < period:
                continue

            ma_values = calculate_ma(data['close'], period)
            ma_current = ma_values.iloc[-1]

            position = 'above' if current_price > ma_current else 'below'

            ma_data[f'ma{period}'] = {
                'value': float(ma_current),
                'position': position,
                'distance_pct': float((current_price - ma_current) / ma_current * 100)
            }

        # 金叉死叉判断（5日和20日均线）
        if 'ma5' in ma_data and 'ma20' in ma_data:
            ma5_values = calculate_ma(data['close'], 5)
            ma20_values = calculate_ma(data['close'], 20)

            if len(ma5_values) >= 2 and len(ma20_values) >= 2:
                # 当前状态
                ma5_now = ma5_values.iloc[-1]
                ma20_now = ma20_values.iloc[-1]

                # 前一天状态
                ma5_prev = ma5_values.iloc[-2]
                ma20_prev = ma20_values.iloc[-2]

                if ma5_prev <= ma20_prev and ma5_now > ma20_now:
                    ma_data['cross'] = 'golden'  # 金叉
                elif ma5_prev >= ma20_prev and ma5_now < ma20_now:
                    ma_data['cross'] = 'death'  # 死叉
                else:
                    ma_data['cross'] = 'none'

        return ma_data

    def _analyze_macd(self, data: pd.DataFrame) -> Dict:
        """MACD 分析"""
        macd_df = calculate_macd(data['close'])

        macd_current = macd_df.iloc[-1]

        result = {
            'macd': float(macd_current['macd']),
            'signal': float(macd_current['signal']),
            'histogram': float(macd_current['histogram']),
        }

        # 判断趋势
        if macd_current['histogram'] > 0:
            result['trend'] = 'bullish'  # 多头
        else:
            result['trend'] = 'bearish'  # 空头

        # 判断金叉死叉
        if len(macd_df) >= 2:
            prev = macd_df.iloc[-2]

            if prev['macd'] <= prev['signal'] and macd_current['macd'] > macd_current['signal']:
                result['cross'] = 'golden'
            elif prev['macd'] >= prev['signal'] and macd_current['macd'] < macd_current['signal']:
                result['cross'] = 'death'
            else:
                result['cross'] = 'none'

        return result

    def _analyze_rsi(self, data: pd.DataFrame) -> Dict:
        """RSI 分析"""
        rsi_period = self.config.get('analysis.indicators.rsi.period', 14)
        overbought = self.config.get('analysis.indicators.rsi.overbought', 70)
        oversold = self.config.get('analysis.indicators.rsi.oversold', 30)

        rsi_values = calculate_rsi(data['close'], rsi_period)
        rsi_current = rsi_values.iloc[-1]

        result = {
            'value': float(rsi_current),
            'overbought_line': overbought,
            'oversold_line': oversold,
        }

        # 判断状态
        if rsi_current > overbought:
            result['status'] = 'overbought'  # 超买
        elif rsi_current < oversold:
            result['status'] = 'oversold'  # 超卖
        else:
            result['status'] = 'normal'

        return result

    def _analyze_bollinger(self, data: pd.DataFrame) -> Dict:
        """布林带分析"""
        bb_period = self.config.get('analysis.indicators.bollinger.period', 20)
        bb_std = self.config.get('analysis.indicators.bollinger.std_dev', 2.0)

        bb_df = calculate_bollinger_bands(data['close'], bb_period, bb_std)

        bb_current = bb_df.iloc[-1]
        current_price = data.iloc[-1]['close']

        result = {
            'upper': float(bb_current['upper']),
            'middle': float(bb_current['middle']),
            'lower': float(bb_current['lower']),
            'current_price': float(current_price),
        }

        # 判断位置
        if current_price > bb_current['upper']:
            result['position'] = 'above_upper'  # 超出上轨
        elif current_price < bb_current['lower']:
            result['position'] = 'below_lower'  # 超出下轨
        else:
            result['position'] = 'within'  # 在轨道内

        return result

    def _generate_signal(self, analysis: Dict) -> str:
        """
        生成综合信号

        Args:
            analysis: 分析结果

        Returns:
            信号 ('buy', 'sell', 'hold')
        """
        buy_signals = 0
        sell_signals = 0

        # MA 信号
        if 'ma' in analysis and 'cross' in analysis['ma']:
            if analysis['ma']['cross'] == 'golden':
                buy_signals += 2
            elif analysis['ma']['cross'] == 'death':
                sell_signals += 2

        # MACD 信号
        if 'macd' in analysis:
            if analysis['macd'].get('cross') == 'golden':
                buy_signals += 2
            elif analysis['macd'].get('cross') == 'death':
                sell_signals += 2

            if analysis['macd'].get('trend') == 'bullish':
                buy_signals += 1
            elif analysis['macd'].get('trend') == 'bearish':
                sell_signals += 1

        # RSI 信号
        if 'rsi' in analysis:
            if analysis['rsi'].get('status') == 'oversold':
                buy_signals += 1
            elif analysis['rsi'].get('status') == 'overbought':
                sell_signals += 1

        # 布林带信号
        if 'bollinger' in analysis:
            if analysis['bollinger'].get('position') == 'below_lower':
                buy_signals += 1
            elif analysis['bollinger'].get('position') == 'above_upper':
                sell_signals += 1

        # 综合判断
        if buy_signals > sell_signals + 1:
            return 'buy'
        elif sell_signals > buy_signals + 1:
            return 'sell'
        else:
            return 'hold'
