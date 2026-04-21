#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试NBA API的PlayByPlayV2端点
"""
import json
import logging
from nba_api.stats.endpoints import PlayByPlayV2
from nba_api.stats.static import teams

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_playbyplay():
    """测试PlayByPlayV2端点"""
    # 获取湖人的球队ID
    lakers = teams.find_team_by_abbreviation('LAL')
    if not lakers:
        logger.error("找不到湖人队")
        return
    
    team_id = lakers['id']
    logger.info(f"湖人队ID: {team_id}")
    
    # 测试不同的比赛ID
    test_game_ids = [
        '0022500801',  # 2025-26赛季湖人比赛
        '0022500802',  # 另一场比赛
        '0022500001'   # 赛季第一场比赛
    ]
    
    for game_id in test_game_ids:
        logger.info(f"\n测试比赛ID: {game_id}")
        try:
            # 直接使用PlayByPlayV2
            pbp = PlayByPlayV2(game_id=game_id)
            
            # 先获取原始响应
            response = pbp.get_response()
            logger.info(f"响应状态码: {response.status_code}")
            
            # 尝试获取JSON数据
            try:
                json_data = response.json()
                logger.info(f"JSON数据获取成功，包含 {len(json_data.get('resultSets', []))} 个结果集")
                
                # 检查resultSets
                if 'resultSets' in json_data:
                    for i, result_set in enumerate(json_data['resultSets']):
                        logger.info(f"结果集 {i}: {result_set.get('name')}, 行数: {len(result_set.get('rowSet', []))}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                # 打印原始响应内容的前1000个字符
                response_text = response.text
                logger.info(f"原始响应内容前1000字符: {response_text[:1000]}")
                
                # 检查是否有HTML错误页面
                if '<html' in response_text.lower():
                    logger.warning("API返回了HTML错误页面，可能是API限制或认证问题")
            
            # 尝试使用get_data_frames
            try:
                data_frames = pbp.get_data_frames()
                logger.info(f"get_data_frames()成功，返回 {len(data_frames)} 个DataFrame")
                for i, df in enumerate(data_frames):
                    logger.info(f"DataFrame {i}: {df.shape} 行x列")
                    logger.info(f"前5行:\n{df.head()}")
            except Exception as e:
                logger.error(f"get_data_frames()失败: {e}")
                
        except Exception as e:
            logger.error(f"测试PlayByPlayV2失败: {e}")
        
        print("-" * 80)

def test_playbyplay_v3():
    """测试PlayByPlayV3端点（如果可用）"""
    logger.info("\n测试PlayByPlayV3端点")
    try:
        from nba_api.stats.endpoints import PlayByPlayV3
        
        test_game_id = '0022500801'
        pbp = PlayByPlayV3(game_id=test_game_id)
        
        # 直接尝试获取数据框
        data_frames = pbp.get_data_frames()
        logger.info(f"get_data_frames()成功，返回 {len(data_frames)} 个DataFrame")
        for i, df in enumerate(data_frames):
            logger.info(f"DataFrame {i}: {df.shape} 行x列")
            if not df.empty:
                logger.info(f"列名: {list(df.columns)}")
                logger.info(f"前5行:\n{df.head()}")
        
    except ImportError:
        logger.warning("PlayByPlayV3不可用")
    except Exception as e:
        logger.error(f"测试PlayByPlayV3失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_playbyplay()
    test_playbyplay_v3()