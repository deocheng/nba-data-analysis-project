#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basketball Reference爬取器 - 用于从Basketball Reference网站获取数据
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasketballReferenceScraper:
    """Basketball Reference爬取器类"""
    
    def __init__(self, max_retries=3, base_delay=2):
        """
        初始化Basketball Reference爬取器
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.base_url = "https://www.basketball-reference.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        带指数退避的重试机制
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        for retry in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"尝试 {retry+1}/{self.max_retries} 失败: {e}")
                if retry < self.max_retries - 1:
                    delay = self.base_delay * (2 ** retry)
                    logger.info(f"{delay}秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"达到最大重试次数，操作失败: {e}")
                    raise
    
    def _get_soup(self, url):
        """
        获取页面的BeautifulSoup对象
        
        Args:
            url: 页面URL
            
        Returns:
            BeautifulSoup对象
        """
        def _fetch():
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        
        return self._retry_with_backoff(_fetch)
    
    def get_team_stats(self, team_abbr, season):
        """
        获取球队赛季统计数据
        
        Args:
            team_abbr: 球队缩写，如 'LAL'
            season: 赛季，如 '2023-24'
            
        Returns:
            球队统计数据
        """
        season_end = season.split('-')[1]
        url = f"{self.base_url}/teams/{team_abbr}/{season_end}.html"
        
        def _get_stats():
            soup = self._get_soup(url)
            
            # 查找统计表格
            table = soup.find('table', id='team_and_opponent')
            if not table:
                raise Exception("找不到统计表格")
            
            # 解析表格数据
            df = pd.read_html(str(table))[0]
            return df
        
        return self._retry_with_backoff(_get_stats)
    
    def get_player_stats(self, player_id, season):
        """
        获取球员赛季统计数据
        
        Args:
            player_id: 球员ID，如 'jamesle01'
            season: 赛季，如 '2023-24'
            
        Returns:
            球员统计数据
        """
        season_end = season.split('-')[1]
        url = f"{self.base_url}/players/{player_id[0]}/{player_id}.html"
        
        def _get_stats():
            soup = self._get_soup(url)
            
            # 查找赛季统计表格
            table = soup.find('table', id=f'per_game.{season_end}')
            if not table:
                raise Exception(f"找不到 {season} 赛季的统计表格")
            
            # 解析表格数据
            df = pd.read_html(str(table))[0]
            return df
        
        return self._retry_with_backoff(_get_stats)
    
    def get_team_schedule(self, team_abbr, season):
        """
        获取球队赛季赛程
        
        Args:
            team_abbr: 球队缩写，如 'LAL'
            season: 赛季，如 '2023-24'
            
        Returns:
            球队赛程数据
        """
        season_end = season.split('-')[1]
        url = f"{self.base_url}/teams/{team_abbr}/{season_end}_games.html"
        
        def _get_schedule():
            soup = self._get_soup(url)
            
            # 查找赛程表格
            table = soup.find('table', id='games')
            if not table:
                raise Exception("找不到赛程表格")
            
            # 解析表格数据
            df = pd.read_html(str(table))[0]
            return df
        
        return self._retry_with_backoff(_get_schedule)
    
    def get_player_gamelog(self, player_id, season):
        """
        获取球员比赛日志
        
        Args:
            player_id: 球员ID，如 'jamesle01'
            season: 赛季，如 '2023-24'
            
        Returns:
            球员比赛日志数据
        """
        season_end = season.split('-')[1]
        url = f"{self.base_url}/players/{player_id[0]}/{player_id}/gamelog/{season_end}"
        
        def _get_gamelog():
            soup = self._get_soup(url)
            
            # 查找比赛日志表格
            table = soup.find('table', id='pgl_basic')
            if not table:
                raise Exception("找不到比赛日志表格")
            
            # 解析表格数据
            df = pd.read_html(str(table))[0]
            return df
        
        return self._retry_with_backoff(_get_gamelog)
    
    def get_standings(self, season):
        """
        获取赛季排名
        
        Args:
            season: 赛季，如 '2023-24'
            
        Returns:
            赛季排名数据
        """
        season_end = season.split('-')[1]
        url = f"{self.base_url}/leagues/NBA_{season_end}_standings.html"
        
        def _get_standings():
            soup = self._get_soup(url)
            
            # 查找东部联盟排名表格
            east_table = soup.find('table', id='confs_standings_E')
            # 查找西部联盟排名表格
            west_table = soup.find('table', id='confs_standings_W')
            
            if not east_table or not west_table:
                raise Exception("找不到排名表格")
            
            # 解析表格数据
            east_df = pd.read_html(str(east_table))[0]
            west_df = pd.read_html(str(west_table))[0]
            
            return {'east': east_df, 'west': west_df}
        
        return self._retry_with_backoff(_get_standings)

if __name__ == "__main__":
    # 测试Basketball Reference爬取器
    scraper = BasketballReferenceScraper()
    
    # 测试获取湖人(LAL)的2023-24赛季数据
    try:
        team_stats = scraper.get_team_stats('LAL', '2023-24')
        print("球队统计数据获取成功:")
        print(team_stats.head())
    except Exception as e:
        print(f"测试失败: {e}")