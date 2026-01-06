"""市场基本面分析模块 - 政策面、资金面、机构持仓、企业关联"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import akshare as ak
import re

from src.core.exceptions import DataProviderError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FundamentalAnalyzer:
    """基本面分析器 - 政策面、资金面、机构持仓、企业关联"""

    def __init__(self):
        """初始化"""
        logger.info("FundamentalAnalyzer initialized")

    def get_fund_flow(self, symbol: str) -> Dict:
        """
        获取资金流向数据

        Args:
            symbol: 股票代码（不带后缀）

        Returns:
            资金流向字典
        """
        symbol_code = symbol.split('.')[0] if '.' in symbol else symbol

        try:
            # 获取个股资金流向
            df = ak.stock_individual_fund_flow_rank(indicator="今日")

            # 筛选指定股票
            stock_flow = df[df['代码'] == symbol_code]

            if stock_flow.empty:
                logger.warning(f"No fund flow data for {symbol}")
                return {}

            row = stock_flow.iloc[0]

            # 列名可能有"今日"前缀
            def get_col_value(col_name):
                """尝试不同的列名格式"""
                for prefix in ['今日', '']:
                    full_name = f'{prefix}{col_name}'
                    if full_name in row.index:
                        return float(row[full_name]) if pd.notna(row[full_name]) else 0.0
                return 0.0

            fund_flow = {
                'main_net_inflow': get_col_value('主力净流入-净额'),
                'main_net_inflow_pct': get_col_value('主力净流入-净占比'),
                'super_large_net_inflow': get_col_value('超大单净流入-净额'),
                'super_large_net_inflow_pct': get_col_value('超大单净流入-净占比'),
                'large_net_inflow': get_col_value('大单净流入-净额'),
                'large_net_inflow_pct': get_col_value('大单净流入-净占比'),
                'medium_net_inflow': get_col_value('中单净流入-净额'),
                'medium_net_inflow_pct': get_col_value('中单净流入-净占比'),
                'small_net_inflow': get_col_value('小单净流入-净额'),
                'small_net_inflow_pct': get_col_value('小单净流入-净占比'),
            }

            logger.info(f"Got fund flow for {symbol}")
            return fund_flow

        except Exception as e:
            logger.error(f"Failed to get fund flow for {symbol}: {e}")
            return {}

    def get_holder_info(self, symbol: str) -> Dict:
        """
        获取股东持股信息

        Args:
            symbol: 股票代码

        Returns:
            持股信息字典
        """
        symbol_code = symbol.split('.')[0] if '.' in symbol else symbol

        try:
            # 获取十大流通股东
            df = ak.stock_gdfx_free_top_10_em(symbol=symbol_code)

            if df.empty:
                logger.warning(f"No holder info for {symbol}")
                return {}

            # 最新一期数据
            latest_date = df['截止日期'].max()
            latest_data = df[df['截止日期'] == latest_date]

            # 统计机构类型
            holder_types = latest_data['股东名称'].str.contains('基金|社保|QFII|保险|券商|信托', na=False)
            institutional_count = holder_types.sum()
            total_holders = len(latest_data)

            # 计算持股比例
            total_holding_pct = latest_data['持股数量占流通股比'].sum()

            holder_info = {
                'report_date': latest_date,
                'total_top10_holders': total_holders,
                'institutional_holders': int(institutional_count),
                'total_holding_pct': float(total_holding_pct),
                'top_holders': []
            }

            # 前5大股东
            for _, row in latest_data.head(5).iterrows():
                holder_info['top_holders'].append({
                    'name': row['股东名称'],
                    'holding_pct': float(row['持股数量占流通股比']),
                    'shares': int(row['持股数量'])
                })

            logger.info(f"Got holder info for {symbol}")
            return holder_info

        except Exception as e:
            logger.error(f"Failed to get holder info for {symbol}: {e}")
            return {}

    def get_holder_changes(self, symbol: str) -> Dict:
        """
        获取股东增减持信息

        Args:
            symbol: 股票代码

        Returns:
            增减持信息字典
        """
        symbol_code = symbol.split('.')[0] if '.' in symbol else symbol

        try:
            # 获取股东增减持数据
            df = ak.stock_ggcg_em(symbol=symbol_code)

            if df.empty:
                logger.warning(f"No holder changes for {symbol}")
                return {}

            # 最近6个月的数据
            recent_data = df.head(10)

            changes = {
                'recent_changes': [],
                'net_change_summary': 0
            }

            for _, row in recent_data.iterrows():
                change_info = {
                    'date': row['变动日期'],
                    'holder_name': row['股东名称'],
                    'change_type': row['变动方向'],
                    'change_shares': float(row.get('变动股本', 0)),
                    'change_pct': float(row.get('变动比例', 0)),
                }
                changes['recent_changes'].append(change_info)

                # 累计净变化（增持为正，减持为负）
                if row['变动方向'] == '增持':
                    changes['net_change_summary'] += float(row.get('变动比例', 0))
                elif row['变动方向'] == '减持':
                    changes['net_change_summary'] -= float(row.get('变动比例', 0))

            logger.info(f"Got holder changes for {symbol}")
            return changes

        except Exception as e:
            logger.error(f"Failed to get holder changes for {symbol}: {e}")
            return {}

    def analyze_fundamental(self, symbol: str) -> Dict:
        """
        综合基本面分析

        Args:
            symbol: 股票代码

        Returns:
            综合分析结果
        """
        analysis = {
            'symbol': symbol,
            'fund_flow': self.get_fund_flow(symbol),
            'holder_info': self.get_holder_info(symbol),
            'holder_changes': self.get_holder_changes(symbol),
        }

        # 资金面评分
        fund_score = 0
        if analysis['fund_flow']:
            main_inflow = analysis['fund_flow'].get('main_net_inflow', 0)
            if main_inflow > 0:
                fund_score = 1
            elif main_inflow < 0:
                fund_score = -1

        # 机构持仓评分
        holder_score = 0
        if analysis['holder_info']:
            inst_ratio = analysis['holder_info'].get('institutional_holders', 0) / max(
                analysis['holder_info'].get('total_top10_holders', 1), 1
            )
            if inst_ratio > 0.5:
                holder_score = 1
            elif inst_ratio > 0.3:
                holder_score = 0.5

        # 增减持评分
        change_score = 0
        if analysis['holder_changes']:
            net_change = analysis['holder_changes'].get('net_change_summary', 0)
            if net_change > 1:
                change_score = 1
            elif net_change > 0:
                change_score = 0.5
            elif net_change < -1:
                change_score = -1

        # 综合评分
        total_score = fund_score + holder_score + change_score

        if total_score >= 2:
            rating = '强烈看好'
        elif total_score >= 1:
            rating = '看好'
        elif total_score >= 0:
            rating = '中性'
        elif total_score >= -1:
            rating = '看淡'
        else:
            rating = '看空'

        analysis['fundamental_rating'] = {
            'fund_score': fund_score,
            'holder_score': holder_score,
            'change_score': change_score,
            'total_score': total_score,
            'rating': rating
        }

        return analysis

    def get_concept_boards(self, symbol: str) -> List[Dict]:
        """
        获取所属概念板块

        Args:
            symbol: 股票代码

        Returns:
            概念板块列表
        """
        symbol_code = symbol.split('.')[0] if '.' in symbol else symbol

        try:
            # 获取股票所属概念
            df = ak.stock_board_concept_cons_em(symbol=symbol_code)

            if df.empty:
                logger.warning(f"No concept boards for {symbol}")
                return []

            concepts = []
            for _, row in df.head(20).iterrows():  # 取前20个概念
                concepts.append({
                    'name': row['板块名称'],
                    'code': row.get('板块代码', ''),
                })

            logger.info(f"Got {len(concepts)} concepts for {symbol}")
            return concepts

        except Exception as e:
            logger.error(f"Failed to get concept boards for {symbol}: {e}")
            return []

    def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        获取公司最新新闻

        Args:
            symbol: 股票代码
            limit: 新闻数量

        Returns:
            新闻列表
        """
        symbol_code = symbol.split('.')[0] if '.' in symbol else symbol

        try:
            # 获取个股新闻
            df = ak.stock_news_em(symbol=symbol_code)

            if df.empty:
                logger.warning(f"No news for {symbol}")
                return []

            news_list = []
            for _, row in df.head(limit).iterrows():
                news_list.append({
                    'title': row['新闻标题'],
                    'date': row['发布时间'],
                    'content': row.get('新闻内容', '')[:200],  # 前200字
                    'url': row.get('新闻链接', ''),
                })

            logger.info(f"Got {len(news_list)} news for {symbol}")
            return news_list

        except Exception as e:
            logger.error(f"Failed to get news for {symbol}: {e}")
            return []

    def extract_hidden_info(self, symbol: str, stock_name: str) -> Dict:
        """
        提取隐藏的深度信息（对外投资、关联企业等）

        Args:
            symbol: 股票代码
            stock_name: 股票名称

        Returns:
            深度信息字典
        """
        hidden_info = {
            'investments': [],
            'related_concepts': [],
            'hot_keywords': [],
            'investment_details': [],  # 新增：详细的投资信息
        }

        try:
            # 1. 从概念板块推断关联
            concepts = self.get_concept_boards(symbol)
            hidden_info['related_concepts'] = [c['name'] for c in concepts]

            # 2. 从新闻中提取关键信息
            news = self.get_company_news(symbol, limit=20)

            # 提取投资、参股等关键词
            investment_keywords = ['投资', '参股', '控股', '收购', '入股', '持股', '战略合作', '持有']

            # 改进的公司名称匹配模式
            company_patterns = [
                re.compile(r'([A-Z\u4e00-\u9fa5]{2,15}(?:公司|科技|集团|股份|有限|企业))'),
                re.compile(r'([\u4e00-\u9fa5]{2,6}(?:航天|卫星|火箭|能源|科技))'),  # 特殊行业
            ]

            # 持股比例模式
            stake_pattern = re.compile(r'持(?:有|股).*?(\d+\.?\d*)%')

            investments_found = {}  # 改为字典，记录详细信息
            hot_keywords_found = set()

            for n in news:
                title = n['title']
                content = n.get('content', '')
                full_text = title + content

                # 查找投资相关
                if any(kw in full_text for kw in investment_keywords):
                    # 提取公司名称
                    all_companies = set()
                    for pattern in company_patterns:
                        companies = pattern.findall(full_text)
                        all_companies.update(companies)

                    for company in all_companies:
                        if company != stock_name and len(company) > 2:
                            # 尝试提取持股比例
                            stake_match = stake_pattern.search(full_text)
                            stake_pct = stake_match.group(1) if stake_match else None

                            if company not in investments_found:
                                investments_found[company] = {
                                    'name': company,
                                    'stake': stake_pct,
                                    'source': title,
                                    'date': n['date']
                                }

                # 提取热点关键词（如航天、新能源等）
                hot_patterns = ['航天', '卫星', '火箭', '太空', '新能源', '风电', '光伏',
                               'AI', '人工智能', '芯片', '半导体', '军工', '国防', '量子']
                for pattern in hot_patterns:
                    if pattern in full_text:
                        hot_keywords_found.add(pattern)

            # 整理投资信息
            hidden_info['investments'] = list(investments_found.keys())[:10]
            hidden_info['investment_details'] = list(investments_found.values())[:10]
            hidden_info['hot_keywords'] = list(hot_keywords_found)

            logger.info(f"Extracted hidden info for {symbol}: {len(investments_found)} investments, {len(hot_keywords_found)} keywords")

        except Exception as e:
            logger.error(f"Failed to extract hidden info for {symbol}: {e}")

        return hidden_info

    def analyze_deep(self, symbol: str, stock_name: str = None) -> Dict:
        """
        深度分析 - 包含隐藏信息挖掘

        Args:
            symbol: 股票代码
            stock_name: 股票名称（可选）

        Returns:
            深度分析结果
        """
        # 如果没有提供股票名称，尝试获取
        if not stock_name:
            try:
                df = ak.stock_zh_a_spot_em()
                symbol_code = symbol.split('.')[0] if '.' in symbol else symbol
                stock_data = df[df['代码'] == symbol_code]
                if not stock_data.empty:
                    stock_name = stock_data.iloc[0]['名称']
            except:
                stock_name = symbol

        analysis = {
            'symbol': symbol,
            'name': stock_name,
            'concepts': self.get_concept_boards(symbol),
            'news': self.get_company_news(symbol, limit=10),
            'hidden_info': self.extract_hidden_info(symbol, stock_name),
        }

        return analysis
