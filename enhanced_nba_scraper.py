#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的NBA数据爬取系统 - 整合多个数据源
"""
import pandas as pd
import numpy as np
import requests
from nba_api.stats.endpoints import (
    PlayerGameLog, TeamGameLog, LeagueDashTeamStats,
    PlayerCareerStats, CommonTeamRoster,
    PlayerProfileV2, TeamInfoCommon,
    PlayByPlayV3
)
from nba_api.stats.static import players, teams
import matplotlib.pyplot as plt
import json
import os
import time
import logging
from datetime import datetime
from cache_manager import CacheManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedNBAScraper:
    """增强的NBA数据爬取类"""

    def __init__(self):
        self.cache_dir = "nba_data/cache"
        self.output_dir = "nba_data"
        self._ensure_directories()
        self.retry_count = 3
        self.retry_delay = 2
        self.cache = CacheManager(cache_dir=self.cache_dir, cache_ttl=24)

    def _ensure_directories(self):
        """确保目录存在"""
        for directory in [self.cache_dir, self.output_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def _retry_request(self, func, *args, **kwargs):
        """带重试的请求"""
        endpoint_name = kwargs.pop('endpoint_name', 'unknown')
        
        for attempt in range(self.retry_count):
            try:
                logger.info(f"执行请求 {endpoint_name} (尝试 {attempt + 1}/{self.retry_count})")
                result = func(*args, **kwargs)
                logger.info(f"请求 {endpoint_name} 成功")
                return result
            except requests.exceptions.Timeout as e:
                logger.warning(f"请求 {endpoint_name} 超时 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    delay = self.retry_delay * (attempt + 1) * 2  # 指数退避
                    logger.info(f"等待 {delay} 秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"请求 {endpoint_name} 最终失败: 超时")
                    raise e
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"请求 {endpoint_name} 连接错误 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    delay = self.retry_delay * (attempt + 1) * 1.5
                    logger.info(f"等待 {delay} 秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"请求 {endpoint_name} 最终失败: 连接错误")
                    raise e
            except Exception as e:
                logger.warning(f"请求 {endpoint_name} 失败 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    delay = self.retry_delay * (attempt + 1)
                    logger.info(f"等待 {delay} 秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"请求 {endpoint_name} 最终失败: {e}")
                    raise e

    def get_all_players(self):
        """获取所有球员信息"""
        return players.get_players()

    def get_all_teams(self):
        """获取所有球队信息"""
        return teams.get_teams()

    def find_player_by_name(self, name):
        """根据姓名查找球员"""
        return players.find_players_by_full_name(name)

    def find_team_by_abbr(self, abbr):
        """根据缩写查找球队"""
        return teams.find_team_by_abbreviation(abbr)

    def get_player_game_log(self, player_id, season, season_type="Regular Season"):
        """获取球员比赛日志"""
        logger.info(f"获取球员 {player_id} 的 {season} 赛季比赛日志")

        # 尝试从缓存获取
        cache_key = f"player_game_log"
        cached_data = self.cache.get(cache_key, 
                                   player_id=player_id, 
                                   season=season, 
                                   season_type=season_type)
        
        if cached_data:
            # 从缓存数据重建DataFrame
            return pd.DataFrame(cached_data)

        def fetch_data():
            game_log = PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star=season_type
            )
            return game_log.get_data_frames()[0]

        try:
            df = self._retry_request(fetch_data, endpoint_name="PlayerGameLog")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              player_id=player_id, 
                              season=season, 
                              season_type=season_type)
            
            return df
        except Exception as e:
            logger.error(f"获取球员比赛日志失败: {e}")
            return pd.DataFrame()

    def get_team_game_log(self, team_id, season, season_type="Regular Season"):
        """获取球队比赛日志"""
        logger.info(f"获取球队 {team_id} 的 {season} 赛季比赛日志")

        # 尝试从缓存获取
        cache_key = f"team_game_log"
        cached_data = self.cache.get(cache_key, 
                                   team_id=team_id, 
                                   season=season, 
                                   season_type=season_type)
        
        if cached_data:
            return pd.DataFrame(cached_data)

        def fetch_data():
            game_log = TeamGameLog(
                team_id=team_id,
                season=season,
                season_type_all_star=season_type
            )
            return game_log.get_data_frames()[0]

        try:
            df = self._retry_request(fetch_data, endpoint_name="TeamGameLog")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              team_id=team_id, 
                              season=season, 
                              season_type=season_type)
            
            return df
        except Exception as e:
            logger.error(f"获取球队比赛日志失败: {e}")
            return pd.DataFrame()

    def get_league_team_stats(self, season, per_mode="PerGame", season_type="Regular Season"):
        """获取联盟球队统计数据"""
        logger.info(f"获取 {season} 赛季联盟球队统计数据")

        # 尝试从缓存获取
        cache_key = f"league_team_stats"
        cached_data = self.cache.get(cache_key, 
                                   season=season, 
                                   per_mode=per_mode, 
                                   season_type=season_type)
        
        if cached_data:
            return pd.DataFrame(cached_data)

        def fetch_data():
            stats = LeagueDashTeamStats(
                season=season,
                per_mode=per_mode,
                season_type=season_type
            )
            return stats.get_data_frames()[0]

        try:
            df = self._retry_request(fetch_data, endpoint_name="LeagueDashTeamStats")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              season=season, 
                              per_mode=per_mode, 
                              season_type=season_type)
            
            return df
        except Exception as e:
            logger.error(f"获取联盟球队统计数据失败: {e}")
            return pd.DataFrame()

    def get_player_career_stats(self, player_id):
        """获取球员职业生涯统计"""
        logger.info(f"获取球员 {player_id} 的职业生涯统计")

        # 尝试从缓存获取
        cache_key = f"player_career_stats"
        cached_data = self.cache.get(cache_key, player_id=player_id)
        
        if cached_data:
            return pd.DataFrame(cached_data)

        def fetch_data():
            career = PlayerCareerStats(player_id=player_id)
            return career.get_data_frames()[0]

        try:
            df = self._retry_request(fetch_data, endpoint_name="PlayerCareerStats")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              player_id=player_id)
            
            return df
        except Exception as e:
            logger.error(f"获取球员职业生涯统计失败: {e}")
            return pd.DataFrame()

    def get_team_info(self, team_id):
        """获取球队详细信息"""
        logger.info(f"获取球队 {team_id} 的详细信息")

        # 尝试从缓存获取
        cache_key = f"team_info"
        cached_data = self.cache.get(cache_key, team_id=team_id)
        
        if cached_data:
            return pd.DataFrame(cached_data)

        def fetch_data():
            team_info = TeamInfoCommon(team_id=team_id)
            return team_info.get_data_frames()[0]

        try:
            df = self._retry_request(fetch_data, endpoint_name="TeamInfoCommon")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              team_id=team_id)
            
            return df
        except Exception as e:
            logger.error(f"获取球队信息失败: {e}")
            return pd.DataFrame()

    def get_team_roster(self, team_id, season):
        """获取球队阵容"""
        logger.info(f"获取球队 {team_id} 的 {season} 赛季阵容")

        # 尝试从缓存获取
        cache_key = f"team_roster"
        cached_data = self.cache.get(cache_key, 
                                   team_id=team_id, 
                                   season=season)
        
        if cached_data:
            return pd.DataFrame(cached_data)

        def fetch_data():
            roster = CommonTeamRoster(team_id=team_id, season=season)
            return roster.get_data_frames()[0]

        try:
            df = self._retry_request(fetch_data, endpoint_name="CommonTeamRoster")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              team_id=team_id, 
                              season=season)
            
            return df
        except Exception as e:
            logger.error(f"获取球队阵容失败: {e}")
            return pd.DataFrame()

    def get_playbyplay(self, game_id, start_period=0, end_period=0):
        """获取比赛的play-by-play数据"""
        logger.info(f"获取比赛 {game_id} 的play-by-play数据")

        # 尝试从缓存获取
        cache_key = f"playbyplay"
        cached_data = self.cache.get(cache_key, 
                                   game_id=game_id, 
                                   start_period=start_period, 
                                   end_period=end_period)
        
        if cached_data:
            return pd.DataFrame(cached_data)

        def fetch_data():
            pbp = PlayByPlayV3(
                game_id=game_id,
                start_period=str(start_period),
                end_period=str(end_period)
            )
            data_frames = pbp.get_data_frames()
            # 返回第一个DataFrame（包含主要的play-by-play数据）
            return data_frames[0] if data_frames else pd.DataFrame()

        try:
            df = self._retry_request(fetch_data, endpoint_name="PlayByPlayV3")
            
            # 缓存数据
            if not df.empty:
                self.cache.set(cache_key, 
                              df.to_dict('records'), 
                              game_id=game_id, 
                              start_period=start_period, 
                              end_period=end_period)
            
            return df
        except Exception as e:
            logger.error(f"获取play-by-play数据失败: {e}")
            return pd.DataFrame()

    def analyze_lebron_career(self):
        """分析勒布朗·詹姆斯的职业生涯"""
        player_id = 2544

        seasons = [f"{year}-{str(year+1)[-2:]}" for year in range(2003, 2026)]
        season_analysis = {}

        for season in seasons:
            logger.info(f"分析赛季: {season}")

            try:
                game_log_df = self.get_player_game_log(player_id, season)

                if game_log_df.empty:
                    logger.warning(f"赛季 {season} 没有比赛数据")
                    continue

                minutes_played = []
                for _, row in game_log_df.iterrows():
                    if 'MIN' in row and isinstance(row['MIN'], (int, float)):
                        minutes_played.append(row['MIN'])
                    elif 'MIN' in row and isinstance(row['MIN'], str) and ':' in row['MIN']:
                        try:
                            mins, secs = row['MIN'].split(':')
                            total_mins = int(mins) + int(secs) / 60
                            minutes_played.append(total_mins)
                        except ValueError:
                            pass

                if not minutes_played:
                    continue

                avg_minutes = np.mean(minutes_played)
                best_stint_duration = avg_minutes / 4
                best_rest_duration = 2

                season_analysis[season] = {
                    'average_minutes': float(avg_minutes),
                    'total_games': len(game_log_df),
                    'best_stint_duration': float(best_stint_duration),
                    'best_rest_duration': float(best_rest_duration)
                }

                logger.info(f"赛季 {season} 分析完成: 平均出场 {avg_minutes:.1f} 分钟")

                time.sleep(1)

            except Exception as e:
                logger.error(f"分析赛季 {season} 失败: {e}")
                continue

        self.save_analysis('lebron_season_analysis', season_analysis)
        self.plot_lebron_analysis(season_analysis)

        return season_analysis

    def save_analysis(self, filename, data):
        """保存分析结果"""
        output_path = os.path.join(self.output_dir, f"{filename}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"分析结果已保存到 {output_path}")

    def plot_lebron_analysis(self, analysis):
        """绘制勒布朗分析图表"""
        if not analysis:
            return

        seasons = list(analysis.keys())
        avg_minutes = [analysis[s]['average_minutes'] for s in seasons]
        best_stint = [analysis[s]['best_stint_duration'] for s in seasons]
        best_rest = [analysis[s]['best_rest_duration'] for s in seasons]

        plt.figure(figsize=(16, 8))
        plt.plot(seasons, avg_minutes, marker='o', linewidth=2, label='Average Minutes')
        plt.plot(seasons, best_stint, marker='s', linewidth=2, label='Best Stint Duration')
        plt.plot(seasons, best_rest, marker='^', linewidth=2, label='Best Rest Duration')
        plt.title('LeBron James Career Minutes Analysis', fontsize=14)
        plt.xlabel('Season')
        plt.ylabel('Minutes')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'lebron_analysis.png'), dpi=150)
        logger.info("分析图表已保存")

    def get_team_stats_all_seasons(self, team_abbr, start_year=2003, end_year=2026):
        """获取球队多个赛季的统计数据"""
        team = self.find_team_by_abbr(team_abbr)
        if not team:
            logger.error(f"找不到球队: {team_abbr}")
            return {}

        team_id = team['id']
        all_stats = {}

        for year in range(start_year, end_year + 1):
            season = f"{year}-{str(year+1)[-2:]}"
            logger.info(f"获取 {team_abbr} 的 {season} 赛季数据")

            try:
                stats_df = self.get_league_team_stats(season)
                if not stats_df.empty:
                    team_stats = stats_df[stats_df['TEAM_ID'] == team_id]
                    if not team_stats.empty:
                        all_stats[season] = team_stats.to_dict('records')[0]

                time.sleep(1)
            except Exception as e:
                logger.error(f"获取 {season} 赛季数据失败: {e}")
                continue

        return all_stats

if __name__ == "__main__":
    scraper = EnhancedNBAScraper()

    import argparse
    parser = argparse.ArgumentParser(description='NBA数据爬取系统')
    parser.add_argument('--lebron', action='store_true', help='分析勒布朗·詹姆斯职业生涯')
    parser.add_argument('--team', help='爬取球队数据')
    parser.add_argument('--season', default='2025-26', help='赛季')

    args = parser.parse_args()

    if args.lebron:
        scraper.analyze_lebron_career()
    elif args.team:
        scraper.get_team_stats_all_seasons(args.team, 2023, 2026)
    else:
        print("用法:")
        print("  python enhanced_nba_scraper.py --lebron  # 分析勒布朗职业生涯")
        print("  python enhanced_nba_scraper.py --team LAL --season 2025-26  # 爬取球队数据")