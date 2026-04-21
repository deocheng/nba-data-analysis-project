#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量抓取所有NBA球队数据
"""
import logging
import json
import os
from enhanced_nba_scraper import EnhancedNBAScraper
from nba_api.stats.static import teams

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NBADataCollector:
    """NBA数据收集器"""

    def __init__(self, season='2025-26'):
        """
        初始化数据收集器
        
        Args:
            season: 赛季
        """
        self.scraper = EnhancedNBAScraper()
        self.season = season
        self.output_dir = f"nba_data/teams/{season}"
        self._ensure_directories()

    def _ensure_directories(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def get_all_teams(self):
        """获取所有NBA球队"""
        return teams.get_teams()

    def collect_team_data(self, team):
        """收集单个球队的数据"""
        team_id = team['id']
        team_abbr = team['abbreviation']
        team_name = team['full_name']
        
        logger.info(f"\n开始收集 {team_name} ({team_abbr}) 的数据")
        
        team_data = {
            'team_info': {},
            'roster': {},
            'team_stats': {},
            'season': self.season,
            'timestamp': ''
        }
        
        try:
            # 获取球队基本信息
            logger.info(f"获取 {team_name} 的基本信息")
            team_info_df = self.scraper.get_team_info(team_id)
            if not team_info_df.empty:
                team_data['team_info'] = team_info_df.to_dict('records')[0]
            
            # 获取球队阵容
            logger.info(f"获取 {team_name} 的阵容")
            roster_df = self.scraper.get_team_roster(team_id, self.season)
            if not roster_df.empty:
                team_data['roster'] = roster_df.to_dict('records')
            
            # 获取球队统计数据
            logger.info(f"获取 {team_name} 的统计数据")
            # 这里需要从联盟统计数据中过滤出当前球队的数据
            league_stats_df = self.scraper.get_league_team_stats(self.season)
            if not league_stats_df.empty:
                team_stats = league_stats_df[league_stats_df['TEAM_ID'] == team_id]
                if not team_stats.empty:
                    team_data['team_stats'] = team_stats.to_dict('records')[0]
            
            # 获取球队比赛日志
            logger.info(f"获取 {team_name} 的比赛日志")
            team_game_log_df = self.scraper.get_team_game_log(team_id, self.season)
            if not team_game_log_df.empty:
                team_data['game_log'] = team_game_log_df.to_dict('records')
            
            team_data['timestamp'] = team_info_df.iloc[0]['SEASON_YEAR'] if not team_info_df.empty else self.season
            
            # 保存数据
            output_file = os.path.join(self.output_dir, f"{team_abbr}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(team_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"✓ {team_name} 数据收集完成，已保存到 {output_file}")
            
            return team_data
            
        except Exception as e:
            logger.error(f"✗ {team_name} 数据收集失败: {e}")
            return None

    def collect_all_teams(self):
        """收集所有球队的数据"""
        all_teams = self.get_all_teams()
        logger.info(f"开始收集 {len(all_teams)} 支球队的 {self.season} 赛季数据")
        
        results = []
        for team in all_teams:
            try:
                team_data = self.collect_team_data(team)
                if team_data:
                    results.append(team_data)
                
                # 避免API调用过于频繁
                import time
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"处理球队 {team['full_name']} 时出错: {e}")
                continue
        
        logger.info(f"\n数据收集完成，成功收集 {len(results)} 支球队的数据")
        
        # 保存汇总数据
        summary_file = os.path.join(self.output_dir, "all_teams_summary.json")
        summary = {
            'season': self.season,
            'total_teams': len(all_teams),
            'successful_teams': len(results),
            'teams': [{'id': team['id'], 'abbreviation': team['abbreviation'], 'name': team['full_name']} for team in all_teams],
            'timestamp': '2025-26'
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        
        logger.info(f"汇总信息已保存到 {summary_file}")
        
        return results

def main():
    """主函数"""
    collector = NBADataCollector(season='2025-26')
    collector.collect_all_teams()

if __name__ == "__main__":
    main()