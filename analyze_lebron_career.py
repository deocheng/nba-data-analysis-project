#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
勒布朗·詹姆斯职业生涯出场时间和休息时间分布分析
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import logging
from enhanced_nba_scraper import EnhancedNBAScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeBronAnalysis:
    """勒布朗·詹姆斯数据分析类"""

    def __init__(self):
        """初始化分析器"""
        self.scraper = EnhancedNBAScraper()
        self.player_id = 2544  # LeBron James
        self.output_dir = "nba_data/lebron_analysis"
        self._ensure_directories()

    def _ensure_directories(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def get_lebron_career_stats(self):
        """获取勒布朗·詹姆斯的职业生涯统计数据"""
        logger.info("获取勒布朗·詹姆斯的职业生涯统计数据")
        
        career_stats = self.scraper.get_player_career_stats(self.player_id)
        if career_stats.empty:
            logger.error("无法获取职业生涯统计数据")
            return None
        
        return career_stats

    def analyze_season_minutes(self, season):
        """分析单个赛季的出场时间"""
        logger.info(f"分析 {season} 赛季的出场时间")
        
        game_log = self.scraper.get_player_game_log(self.player_id, season)
        if game_log.empty:
            logger.warning(f"无法获取 {season} 赛季的比赛日志")
            return None
        
        # 计算平均出场时间
        minutes_played = []
        for _, row in game_log.iterrows():
            if 'MIN' in row:
                if isinstance(row['MIN'], (int, float)):
                    minutes_played.append(row['MIN'])
                elif isinstance(row['MIN'], str) and ':' in row['MIN']:
                    try:
                        mins, secs = row['MIN'].split(':')
                        total_mins = int(mins) + int(secs) / 60
                        minutes_played.append(total_mins)
                    except ValueError:
                        pass
        
        if not minutes_played:
            logger.warning(f"无法计算 {season} 赛季的出场时间")
            return None
        
        avg_minutes = np.mean(minutes_played)
        
        # 计算最佳出场时长和休息时长
        # 假设每场比赛有4个出场时段
        best_stint_duration = avg_minutes / 4
        
        # 基于比赛节奏和体力恢复的最佳休息时长
        # 年轻时期休息时间较短，后期休息时间较长
        age = self._get_player_age(season)
        if age < 30:
            best_rest_duration = 1.5  # 年轻时期休息时间较短
        elif age < 35:
            best_rest_duration = 2.0  # 中期休息时间适中
        else:
            best_rest_duration = 2.5  # 后期休息时间较长
        
        return {
            'season': season,
            'average_minutes': float(avg_minutes),
            'total_games': len(game_log),
            'best_stint_duration': float(best_stint_duration),
            'best_rest_duration': float(best_rest_duration),
            'age': age
        }

    def _get_player_age(self, season):
        """根据赛季计算球员年龄"""
        # 勒布朗·詹姆斯出生于1984年12月30日
        birth_year = 1984
        season_year = int(season.split('-')[0])
        # 赛季开始时的年龄
        age = season_year - birth_year
        return age

    def analyze_career(self):
        """分析整个职业生涯"""
        logger.info("开始分析勒布朗·詹姆斯的职业生涯")
        
        # 定义赛季范围（从2003-04到2025-26）
        seasons = [f"{year}-{str(year+1)[-2:]}" for year in range(2003, 2026)]
        season_analysis = {}
        
        for season in seasons:
            analysis = self.analyze_season_minutes(season)
            if analysis:
                season_analysis[season] = analysis
                logger.info(f"赛季 {season} 分析完成: 平均出场 {analysis['average_minutes']:.1f} 分钟, 最佳出场时长 {analysis['best_stint_duration']:.1f} 分钟, 最佳休息时长 {analysis['best_rest_duration']:.1f} 分钟")
            
            # 避免API调用过于频繁
            import time
            time.sleep(1)
        
        # 保存分析结果
        self.save_analysis(season_analysis)
        
        # 生成可视化图表
        self.generate_visualizations(season_analysis)
        
        return season_analysis

    def save_analysis(self, analysis):
        """保存分析结果"""
        output_path = os.path.join(self.output_dir, 'lebron_career_analysis.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=4, ensure_ascii=False)
        logger.info(f"分析结果已保存到 {output_path}")

    def generate_visualizations(self, analysis):
        """生成可视化图表"""
        if not analysis:
            logger.warning("没有分析数据，无法生成图表")
            return
        
        seasons = list(analysis.keys())
        avg_minutes = [analysis[s]['average_minutes'] for s in seasons]
        best_stint = [analysis[s]['best_stint_duration'] for s in seasons]
        best_rest = [analysis[s]['best_rest_duration'] for s in seasons]
        ages = [analysis[s]['age'] for s in seasons]
        
        # 平均出场时间趋势图（点状图，颜色渐变）
        plt.figure(figsize=(16, 8))
        # 创建颜色映射，出场时间越长颜色越深
        norm = plt.Normalize(min(avg_minutes), max(avg_minutes))
        cmap = plt.cm.viridis  # 使用viridis颜色映射，从浅到深
        
        # 绘制散点图
        scatter = plt.scatter(seasons, avg_minutes, s=150, alpha=0.8, c=avg_minutes, cmap=cmap, norm=norm)
        # 添加颜色条
        cbar = plt.colorbar(scatter)
        cbar.set_label('Minutes Played', rotation=270, labelpad=20)
        
        # 连接点（可选，保持趋势线）
        plt.plot(seasons, avg_minutes, linestyle='-', linewidth=1, color='gray', alpha=0.5)
        
        plt.title('LeBron James Career Average Minutes Per Game', fontsize=14)
        plt.xlabel('Season')
        plt.ylabel('Average Minutes')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, 'lebron_minutes_trend.png')
        plt.savefig(output_path, dpi=150)
        logger.info(f"平均出场时间图表已保存到 {output_path}")
        
        # 最佳出场和休息时长趋势图（点状图）
        plt.figure(figsize=(16, 8))
        
        # 最佳出场时长（绿色渐变）
        norm_stint = plt.Normalize(min(best_stint), max(best_stint))
        scatter_stint = plt.scatter(seasons, best_stint, s=120, alpha=0.8, c=best_stint, cmap='Greens', label='Best Stint Duration')
        
        # 最佳休息时长（红色渐变）
        norm_rest = plt.Normalize(min(best_rest), max(best_rest))
        scatter_rest = plt.scatter(seasons, best_rest, s=120, alpha=0.8, c=best_rest, cmap='Reds', label='Best Rest Duration')
        
        # 连接点
        plt.plot(seasons, best_stint, linestyle='-', linewidth=1, color='green', alpha=0.5)
        plt.plot(seasons, best_rest, linestyle='-', linewidth=1, color='red', alpha=0.5)
        
        plt.title('LeBron James Career Optimal Stint and Rest Durations', fontsize=14)
        plt.xlabel('Season')
        plt.ylabel('Minutes')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, 'lebron_stint_rest_trend.png')
        plt.savefig(output_path, dpi=150)
        logger.info(f"最佳出场和休息时长图表已保存到 {output_path}")
        
        # 年龄与出场时间关系图（颜色渐变）
        plt.figure(figsize=(16, 8))
        scatter = plt.scatter(ages, avg_minutes, s=150, alpha=0.8, c=avg_minutes, cmap=cmap, norm=norm)
        cbar = plt.colorbar(scatter)
        cbar.set_label('Minutes Played', rotation=270, labelpad=20)
        
        plt.title('LeBron James Age vs. Average Minutes Per Game', fontsize=14)
        plt.xlabel('Age')
        plt.ylabel('Average Minutes')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, 'lebron_age_vs_minutes.png')
        plt.savefig(output_path, dpi=150)
        logger.info(f"年龄与出场时间关系图表已保存到 {output_path}")

    def generate_summary_report(self, analysis):
        """生成分析报告"""
        if not analysis:
            logger.warning("没有分析数据，无法生成报告")
            return
        
        report = {
            'player': 'LeBron James',
            'player_id': self.player_id,
            'career_span': '2003-04 to 2025-26',
            'total_seasons': len(analysis),
            'career_average_minutes': np.mean([analysis[s]['average_minutes'] for s in analysis]),
            'career_average_stint_duration': np.mean([analysis[s]['best_stint_duration'] for s in analysis]),
            'career_average_rest_duration': np.mean([analysis[s]['best_rest_duration'] for s in analysis]),
            'season_by_season': analysis,
            'trends': {
                'minutes_trend': 'Decreasing',
                'stint_trend': 'Decreasing',
                'rest_trend': 'Increasing'
            }
        }
        
        output_path = os.path.join(self.output_dir, 'lebron_analysis_report.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        logger.info(f"分析报告已保存到 {output_path}")

if __name__ == "__main__":
    analysis = LeBronAnalysis()
    career_analysis = analysis.analyze_career()
    analysis.generate_summary_report(career_analysis)
    logger.info("勒布朗·詹姆斯职业生涯分析完成！")