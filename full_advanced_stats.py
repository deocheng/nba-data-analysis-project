"""
完整的NBA高级数据计算器
包含主流高阶数据的详细实现
"""

import math
from typing import Dict, Any, Optional, List
import json
import pandas as pd

class CompleteAdvancedStats:
    """完整的NBA高级数据计算类"""
    
    def __init__(self):
        # 联盟基准数据（2023-24赛季大致值）
        self.league_averages = {
            'pace': 98.0,  # 每48分钟回合数
            'avg_ts': 0.570,
            'avg_efg': 0.540,
            'avg_usg': 20.0,
            'avg_per': 15.0,
            'per_std': 3.0
        }
    
    def calculate_complete_advanced_stats(self, player: Dict, team: Optional[Dict] = None) -> Dict:
        """
        计算完整的高级数据
        
        Args:
            player: 球员数据字典
            team: 球队数据字典（可选）
        
        Returns:
            完整的高级数据字典
        """
        stats = {}
        
        # 基础效率指标
        stats.update(self._calculate_shooting_metrics(player))
        stats.update(self._calculate_usage_metrics(player))
        stats.update(self._calculate_rebound_metrics(player))
        stats.update(self._calculate_playmaking_metrics(player))
        stats.update(self._calculate_defense_metrics(player))
        
        # 综合指标
        stats['PER_simplified'] = self._calculate_simplified_per(player)
        stats['Game_Score'] = self._calculate_game_score(player)
        
        # 如果有球队数据，计算更高级的指标
        if team:
            stats.update(self._calculate_team_relative_metrics(player, team))
        
        return stats
    
    def _calculate_shooting_metrics(self, player: Dict) -> Dict:
        """
        计算投篮相关的高级数据
        
        Includes: eFG%, TS%, 3PAr, FTr, etc.
        """
        metrics = {}
        
        FGM = player.get('FGM', 0)
        FGA = player.get('FGA', 0)
        FG3M = player.get('FG3M', 0)
        FG3A = player.get('FG3A', 0)
        FTM = player.get('FTM', 0)
        FTA = player.get('FTA', 0)
        PTS = player.get('PTS', FGM*2 + FG3M + FTM)
        
        # 有效投篮命中率 (eFG%)
        if FGA > 0:
            metrics['eFG%'] = (FGM + 0.5 * FG3M) / FGA
        else:
            metrics['eFG%'] = 0
        
        # 真实投篮命中率 (TS%)
        if FGA + 0.44 * FTA > 0:
            metrics['TS%'] = PTS / (2 * (FGA + 0.44 * FTA))
        else:
            metrics['TS%'] = 0
        
        # 3分出手比例
        if FGA > 0:
            metrics['3PAr'] = FG3A / FGA
        else:
            metrics['3PAr'] = 0
        
        # 罚球率
        if FGA > 0:
            metrics['FTr'] = FTA / FGA
        else:
            metrics['FTr'] = 0
        
        # 2分命中率
        FG2A = FGA - FG3A
        FG2M = FGM - FG3M
        if FG2A > 0:
            metrics['2P%'] = FG2M / FG2A
        else:
            metrics['2P%'] = 0
        
        # 3分命中率
        if FG3A > 0:
            metrics['3P%'] = FG3M / FG3A
        else:
            metrics['3P%'] = 0
        
        # 罚球命中率
        if FTA > 0:
            metrics['FT%'] = FTM / FTA
        else:
            metrics['FT%'] = 0
        
        return metrics
    
    def _calculate_usage_metrics(self, player: Dict) -> Dict:
        """
        计算使用率相关指标
        """
        metrics = {}
        
        FGA = player.get('FGA', 0)
        FTA = player.get('FTA', 0)
        TOV = player.get('TOV', 0)
        MP = player.get('MP', 0)
        
        # 使用率 (USG%) - 完整公式
        if MP > 0:
            total_poss = FGA + 0.44 * FTA + TOV
            metrics['USG%'] = (total_poss * 100) / (MP * self.league_averages['pace'] / 48)
        else:
            metrics['USG%'] = 0
        
        return metrics
    
    def _calculate_rebound_metrics(self, player: Dict) -> Dict:
        """
        计算篮板相关指标
        """
        metrics = {}
        
        ORB = player.get('ORB', 0)
        DRB = player.get('DRB', 0)
        TRB = player.get('TRB', ORB + DRB)
        MP = player.get('MP', 0)
        
        if MP > 0:
            # 篮板率（简化计算）
            metrics['ORB%'] = (ORB * 100) / MP * 48  # 每48分钟
            metrics['DRB%'] = (DRB * 100) / MP * 48
            metrics['TRB%'] = (TRB * 100) / MP * 48
            
            # 篮板效率
            metrics['ORB_per_36'] = ORB / MP * 36
            metrics['DRB_per_36'] = DRB / MP * 36
            metrics['TRB_per_36'] = TRB / MP * 36
        else:
            metrics['ORB%'] = metrics['DRB%'] = metrics['TRB%'] = 0
            metrics['ORB_per_36'] = metrics['DRB_per_36'] = metrics['TRB_per_36'] = 0
        
        return metrics
    
    def _calculate_playmaking_metrics(self, player: Dict) -> Dict:
        """
        计算组织相关指标
        """
        metrics = {}
        
        AST = player.get('AST', 0)
        TOV = player.get('TOV', 0)
        FGM = player.get('FGM', 0)
        FGA = player.get('FGA', 0)
        MP = player.get('MP', 0)
        
        if MP > 0:
            # 助攻比率
            denominator = FGA + 0.44 * player.get('FTA', 0) + AST + TOV
            if denominator > 0:
                metrics['AST%'] = (AST * 100) / denominator
            else:
                metrics['AST%'] = 0
            
            # 助攻失误比
            if TOV > 0:
                metrics['AST/TOV'] = AST / TOV
            else:
                metrics['AST/TOV'] = AST * 10 if AST > 0 else 0
            
            # 助攻率
            metrics['AST_per_36'] = AST / MP * 36
        else:
            metrics['AST%'] = metrics['AST/TOV'] = metrics['AST_per_36'] = 0
        
        return metrics
    
    def _calculate_defense_metrics(self, player: Dict) -> Dict:
        """
        计算防守相关指标
        """
        metrics = {}
        
        STL = player.get('STL', 0)
        BLK = player.get('BLK', 0)
        PF = player.get('PF', 0)
        MP = player.get('MP', 0)
        
        if MP > 0:
            # 每36分钟数据
            metrics['STL_per_36'] = STL / MP * 36
            metrics['BLK_per_36'] = BLK / MP * 36
            metrics['PF_per_36'] = PF / MP * 36
            
            # 防守积极性指标
            metrics['Defensive_Activity'] = (STL + BLK) / MP * 36
        else:
            metrics['STL_per_36'] = metrics['BLK_per_36'] = 0
            metrics['PF_per_36'] = metrics['Defensive_Activity'] = 0
        
        return metrics
    
    def _calculate_simplified_per(self, player: Dict) -> float:
        """
        计算简化版PER（球员效率值）
        
        真正的PER需要联盟平均数据，这是一个简化版本
        """
        MP = player.get('MP', 0)
        if MP == 0:
            return 0
        
        # 提取数据
        FG = player.get('FGM', 0)
        TP = player.get('FG3M', 0)
        FT = player.get('FTM', 0)
        AST = player.get('AST', 0)
        TRB = player.get('TRB', player.get('ORB', 0) + player.get('DRB', 0))
        STL = player.get('STL', 0)
        BLK = player.get('BLK', 0)
        TOV = player.get('TOV', 0)
        FGA = player.get('FGA', 0)
        FTA = player.get('FTA', 0)
        
        # 计算未经调整的PER
        uPER = (
            FG * 2.0 + TP * 1.0 + FT * 1.0 +
            AST * 1.5 + TRB * 1.2 + STL * 2.0 + BLK * 2.0 -
            TOV * 1.5 - FGA * 0.8 - FTA * 0.4
        )
        
        # 每100分钟
        uPER_per_100 = uPER / MP * 100
        
        # 调整到基准15
        PER = (uPER_per_100 / 67) * 15
        
        return round(PER, 2)
    
    def _calculate_game_score(self, player: Dict) -> float:
        """
        计算Game Score（比赛评分）
        
        这是John Hollinger的另一个指标，用于单场比赛
        """
        PTS = player.get('PTS', 0)
        FG = player.get('FGM', 0)
        FGA = player.get('FGA', 0)
        FT = player.get('FTM', 0)
        FTA = player.get('FTA', 0)
        ORB = player.get('ORB', 0)
        DRB = player.get('DRB', 0)
        TRB = ORB + DRB
        AST = player.get('AST', 0)
        STL = player.get('STL', 0)
        BLK = player.get('BLK', 0)
        PF = player.get('PF', 0)
        TOV = player.get('TOV', 0)
        
        game_score = (
            PTS + 0.4 * FG - 0.7 * FGA - 0.4 * (FTA - FT) +
            0.7 * ORB + 0.3 * DRB + 0.7 * STL + 0.7 * BLK +
            0.1 * AST - 0.4 * PF - 0.4 * TOV
        )
        
        return round(game_score, 2)
    
    def _calculate_team_relative_metrics(self, player: Dict, team: Dict) -> Dict:
        """
        计算与球队相关的指标（简化版）
        """
        metrics = {}
        
        # 这里可以加入更高级的相对指标
        # 如：进攻贡献份额、防守贡献等
        
        return metrics
    
    def generate_player_profile(self, player_name: str, stats: Dict) -> Dict:
        """
        生成球员分析资料
        """
        profile = {
            'name': player_name,
            'ratings': self._rate_player(stats),
            'categories': self._categorize_player(stats),
            'key_strengths': self._identify_strengths(stats),
            'areas_to_improve': self._identify_weaknesses(stats),
            'comparison_baseline': self._compare_to_average(stats)
        }
        return profile
    
    def _rate_player(self, stats: Dict) -> Dict:
        """对球员进行多维度评级"""
        ratings = {}
        
        # 基于PER的整体评级
        PER = stats.get('PER_simplified', 0)
        if PER >= 25:
            ratings['overall'] = "Elite"
        elif PER >= 20:
            ratings['overall'] = "All-Star"
        elif PER >= 15:
            ratings['overall'] = "Starter"
        elif PER >= 10:
            ratings['overall'] = "Rotation"
        else:
            ratings['overall'] = "Bench"
        
        # 得分效率评级
        TS = stats.get('TS%', 0)
        if TS >= 0.60:
            ratings['scoring_efficiency'] = "Elite"
        elif TS >= 0.55:
            ratings['scoring_efficiency'] = "Excellent"
        elif TS >= 0.50:
            ratings['scoring_efficiency'] = "Average"
        else:
            ratings['scoring_efficiency'] = "Below Average"
        
        return ratings
    
    def _categorize_player(self, stats: Dict) -> List[str]:
        """对球员进行类型分类"""
        categories = []
        
        USG = stats.get('USG%', 0)
        AST = stats.get('AST%', 0)
        TS = stats.get('TS%', 0)
        
        if USG > 28 and AST > 20:
            categories.append("Primary Playmaker")
        elif USG > 25:
            categories.append("High-Usage Scorer")
        
        if TS > 0.58:
            categories.append("Efficient Scorer")
        
        return categories
    
    def _identify_strengths(self, stats: Dict) -> List[str]:
        """识别球员的强项"""
        strengths = []
        
        if stats.get('TS%', 0) > 0.55:
            strengths.append("Highly efficient scorer")
        
        if stats.get('eFG%', 0) > 0.52:
            strengths.append("Effective shot selection")
        
        if stats.get('AST%', 0) > 20:
            strengths.append("Strong playmaking")
        
        if stats.get('Defensive_Activity', 0) > 4:
            strengths.append("Active defender")
        
        if stats.get('TRB%', 0) > 15:
            strengths.append("Strong rebounding")
        
        return strengths
    
    def _identify_weaknesses(self, stats: Dict) -> List[str]:
        """识别球员的弱项"""
        weaknesses = []
        
        if stats.get('TS%', 0) < 0.48:
            weaknesses.append("Needs better scoring efficiency")
        
        if stats.get('TOV%', 0) > 14:
            weaknesses.append("High turnover rate")
        
        if stats.get('eFG%', 0) < 0.45:
            weaknesses.append("Needs better shot selection")
        
        return weaknesses
    
    def _compare_to_average(self, stats: Dict) -> Dict:
        """与联盟平均水平比较"""
        comparison = {}
        
        TS_diff = stats.get('TS%', 0) - self.league_averages['avg_ts']
        eFG_diff = stats.get('eFG%', 0) - self.league_averages['avg_efg']
        
        if TS_diff > 0.02:
            comparison['ts_vs_average'] = "Well Above Average"
        elif TS_diff > -0.02:
            comparison['ts_vs_average'] = "Average"
        else:
            comparison['ts_vs_average'] = "Below Average"
        
        if eFG_diff > 0.02:
            comparison['efg_vs_average'] = "Well Above Average"
        elif eFG_diff > -0.02:
            comparison['efg_vs_average'] = "Average"
        else:
            comparison['efg_vs_average'] = "Below Average"
        
        return comparison


def analyze_lebron_advanced():
    """分析LeBron的高级数据演示"""
    
    # 示例LeBron数据（2023-24）
    lebron_data = {
        'GP': 71,
        'MP': 35.2,
        'FGM': 9.2,
        'FGA': 18.6,
        'FG3M': 2.4,
        'FG3A': 6.9,
        'FTM': 4.2,
        'FTA': 5.9,
        'ORB': 1.1,
        'DRB': 6.4,
        'TRB': 7.5,
        'AST': 8.3,
        'STL': 1.3,
        'BLK': 0.6,
        'TOV': 3.5,
        'PF': 1.6,
        'PTS': 25.0
    }
    
    calculator = CompleteAdvancedStats()
    advanced_stats = calculator.calculate_complete_advanced_stats(lebron_data)
    profile = calculator.generate_player_profile("LeBron James", advanced_stats)
    
    result = {
        'basic_stats': lebron_data,
        'advanced_stats': advanced_stats,
        'player_profile': profile
    }
    
    # 保存文件 - 简化路径
    output_file = 'nba_data/lebron_analysis/lebron_full_advanced_stats.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("🏀 LeBron完整高级数据分析完成！")
    print(f"✓ 数据已保存到: {output_file}")
    print("\n📊 关键数据摘要:")
    print(f"   PER: {advanced_stats['PER_simplified']}")
    print(f"   TS%: {advanced_stats['TS%']:.3f}")
    print(f"   eFG%: {advanced_stats['eFG%']:.3f}")
    print(f"   3PAr: {advanced_stats['3PAr']:.3f}")
    print(f"   USG%: {advanced_stats['USG%']:.1f}")
    print(f"   Game Score: {advanced_stats['Game_Score']}")
    print(f"\n🏆 整体评级: {profile['ratings']['overall']}")
    
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("🏀 NBA完整高级数据计算器")
    print("=" * 60)
    print()
    analyze_lebron_advanced()
