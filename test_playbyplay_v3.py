#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PlayByPlayV3数据获取功能
"""
import logging
from enhanced_nba_scraper import EnhancedNBAScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_playbyplay():
    """测试PlayByPlayV3数据获取"""
    scraper = EnhancedNBAScraper()
    
    # 测试不同的比赛ID
    test_game_ids = [
        '0022500801',  # 2025-26赛季湖人比赛
        '0022500802',  # 另一场比赛
        '0022500001'   # 赛季第一场比赛
    ]
    
    for game_id in test_game_ids:
        logger.info(f"\n测试比赛ID: {game_id}")
        try:
            # 获取play-by-play数据
            pbp_df = scraper.get_playbyplay(game_id)
            
            if not pbp_df.empty:
                logger.info(f"成功获取 {len(pbp_df)} 条play-by-play记录")
                logger.info(f"数据列: {list(pbp_df.columns)}")
                logger.info(f"前10条记录:\n{pbp_df.head(10)}")
                
                # 分析数据
                analyze_playbyplay_data(pbp_df, game_id)
            else:
                logger.warning(f"未获取到 {game_id} 的play-by-play数据")
            
        except Exception as e:
            logger.error(f"测试PlayByPlayV3失败: {e}")
        
        print("-" * 80)

def analyze_playbyplay_data(df, game_id):
    """分析play-by-play数据"""
    logger.info(f"分析比赛 {game_id} 的play-by-play数据")
    
    # 统计事件类型
    if 'actionType' in df.columns:
        action_types = df['actionType'].value_counts()
        logger.info(f"事件类型统计:\n{action_types}")
    
    # 统计得分事件
    if 'shotResult' in df.columns:
        shot_results = df['shotResult'].value_counts()
        logger.info(f"投篮结果统计:\n{shot_results}")
    
    # 统计球队
    if 'teamTricode' in df.columns:
        teams = df['teamTricode'].value_counts()
        logger.info(f"球队事件统计:\n{teams}")
    
    # 统计时间段
    if 'period' in df.columns:
        periods = df['period'].value_counts().sort_index()
        logger.info(f"各节事件统计:\n{periods}")

if __name__ == "__main__":
    test_playbyplay()