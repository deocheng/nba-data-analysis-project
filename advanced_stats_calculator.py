"""
NBA高级数据计算器
包含主流的高阶数据计算公式
"""

import math
from typing import Dict, Any, Optional
import json

class AdvancedStatsCalculator:
    """NBA高级数据计算器"""
    
    def __init__(self):
        pass
    
    def calculate_all_stats(self, player_stats: Dict[str, Any], team_stats: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        计算所有高级数据
        
        Args:
            player_stats: 球员统计数据字典
            team_stats: 球队统计数据字典（可选）
        
        Returns:
            包含所有高阶数据的字典
        """
        stats = {}
        
        # 计算基本高阶数据
        stats.update(self.calculate_shooting_efficiency(player_stats))
        stats.update(self.calculate_usage_rates(player_stats))
        stats.update(self.calculate_percentages(player_stats))
        
        # 如果有球队数据，计算更复杂的指标
        if team_stats:
            stats.update(self.calculate_ratings(player_stats, team_stats))
            stats.update(self.calculate_possessions(player_stats, team_stats))
        
        # 计算PER（简化版）
        stats['PER'] = self.calculate_per(player_stats)
        
        return stats
    
    def calculate_shooting_efficiency(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """
        计算投篮效率相关指标
        
        Args:
            stats: 球员统计数据
        
        Returns:
            包含eFG%, TS%等的字典
        """
        results = {}
        
        FGM = stats.get('FGM', 0)
        FGA = stats.get('FGA', 0)
        FG3M = stats.get('FG3M', 0)
        FG3A = stats.get('FG3A', 0)
        FTM = stats.get('FTM', 0)
        FTA = stats.get('FTA', 0)
        
        # 有效投篮命中率 (eFG%)
        if FGA > 0:
            results['eFG%'] = (FGM + 0.5 * FG3M) / FGA
        else:
            results['eFG%'] = 0
        
        # 真实投篮命中率 (TS%)
        if FGA + 0.44 * FTA > 0:
            points = FGM * 2 + FG3M + FTM  # 简化计算
            results['TS%'] = points / (2 * (FGA + 0.44 * FTA))
        else:
            results['TS%'] = 0
        
        # 3分命中率 (3P%)
        if FG3A > 0:
            results['3P%'] = FG3M / FG3A
        else:
            results['3P%'] = 0
        
        # 2分命中率 (2P%)
        FG2A = FGA - FG3A
        FG2M = FGM - FG3M
        if FG2A > 0:
            results['2P%'] = FG2M / FG2A
        else:
            results['2P%'] = 0
        
        # 罚球命中率 (FT%)
        if FTA > 0:
            results['FT%'] = FTM / FTA
        else:
            results['FT%'] = 0
        
        return results
    
    def calculate_usage_rates(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """
        计算使用率相关指标
        
        Args:
            stats: 球员统计数据
        
        Returns:
            包含USG%等的字典
        """
        results = {}
        
        FGA = stats.get('FGA', 0)
        FTA = stats.get('FTA', 0)
        TOV = stats.get('TOV', 0)
        
        # 使用率 (USG%) - 简化计算
        # 实际需要团队数据，这里用简化版本
        usage_numerator = FGA + 0.44 * FTA + TOV
        if usage_numerator > 0:
            results['USG%'] = usage_numerator / (FGA + FTA + TOV + 1) * 100  # 添加1避免0除
        else:
            results['USG%'] = 0
        
        return results
    
    def calculate_percentages(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """
        计算百分比指标（AST%, STL%, BLK%, TOV%, ORB%, DRB%）
        
        Args:
            stats: 球员统计数据
        
        Returns:
            包含各项百分比的字典
        """
        results = {}
        
        MP = stats.get('MP', 0)
        
        if MP > 0:
            # 助攻百分比 (AST%)
            AST = stats.get('AST', 0)
            FGA = stats.get('FGA', 0)
            if FGA > 0:
                results['AST%'] = (AST * 100) / (FGA + 0.44 * stats.get('FTA', 0) + AST + stats.get('TOV', 0))
            else:
                results['AST%'] = 0
            
            # 抢断百分比 (STL%) - 每48分钟抢断数
            STL = stats.get('STL', 0)
            results['STL_per_36'] = STL / MP * 36  # 每36分钟
            
            # 盖帽百分比 (BLK%) - 每48分钟盖帽数
            BLK = stats.get('BLK', 0)
            results['BLK_per_36'] = BLK / MP * 36  # 每36分钟
            
            # 失误百分比 (TOV%)
            TOV = stats.get('TOV', 0)
            FTA = stats.get('FTA', 0)
            if FGA + 0.44 * FTA + TOV > 0:
                results['TOV%'] = (TOV * 100) / (FGA + 0.44 * FTA + TOV)
            else:
                results['TOV%'] = 0
            
            # 进攻篮板 - 每36分钟
            ORB = stats.get('ORB', 0)
            results['ORB_per_36'] = ORB / MP * 36  # 每36分钟
            
            # 防守篮板 - 每36分钟
            DRB = stats.get('DRB', 0)
            results['DRB_per_36'] = DRB / MP * 36  # 每36分钟
        else:
            # 如果没有上场时间，全部为0
            results['AST%'] = 0
            results['STL_per_36'] = 0
            results['BLK_per_36'] = 0
            results['TOV%'] = 0
            results['ORB_per_36'] = 0
            results['DRB_per_36'] = 0
        
        return results
    
    def calculate_ratings(self, player_stats: Dict[str, Any], team_stats: Dict[str, Any]) -> Dict[str, float]:
        """
        计算进攻和防守评分
        
        Args:
            player_stats: 球员统计数据
            team_stats: 球队统计数据
        
        Returns:
            包含ORtg和DRtg的字典
        """
        results = {}
        
        # 进攻评分 (ORtg) - 简化版
        PTS = player_stats.get('PTS', 0)
        AST = player_stats.get('AST', 0)
        FGA = player_stats.get('FGA', 0)
        FTA = player_stats.get('FTA', 0)
        TOV = player_stats.get('TOV', 0)
        
        team_PTS = team_stats.get('PTS', 0)
        team_POSS = team_stats.get('possessions', 100)  # 假设100回合
        
        if team_POSS > 0:
            # 简化版ORtg计算
            results['ORtg'] = (PTS + 0.5 * AST) / team_POSS * 100
        else:
            results['ORtg'] = 0
        
        # 防守评分 (DRtg) - 简化版
        team_DRtg = team_stats.get('DRtg', 100)  # 假设球队DRtg
        results['DRtg'] = team_DRtg
        
        return results
    
    def calculate_possessions(self, player_stats: Dict[str, Any], team_stats: Dict[str, Any]) -> Dict[str, float]:
        """
        计算与回合相关的数据
        
        Args:
            player_stats: 球员统计数据
            team_stats: 球队统计数据
        
        Returns:
            包含相关数据的字典
        """
        results = {}
        
        # 计算球员个人回合数（简化版）
        FGA = player_stats.get('FGA', 0)
        FTA = player_stats.get('FTA', 0)
        TOV = player_stats.get('TOV', 0)
        ORB = player_stats.get('ORB', 0)
        
        player_poss = FGA + 0.44 * FTA + TOV - 1.07 * (ORB / (ORB + player_stats.get('DRB', 0) + 1))
        
        results['POSS'] = player_poss
        
        return results
    
    def calculate_per(self, stats: Dict[str, Any]) -> float:
        """
        计算PER（球员效率值）- 简化版
        
        这是一个简化版本的PER计算，实际的PER需要联盟平均数据
        
        Args:
            stats: 球员统计数据
        
        Returns:
            PER值
        """
        # 获取基础数据
        FG = stats.get('FGM', 0)
        TP = stats.get('FG3M', 0)
        FT = stats.get('FTM', 0)
        AST = stats.get('AST', 0)
        TRB = stats.get('TRB', 0)
        STL = stats.get('STL', 0)
        BLK = stats.get('BLK', 0)
        TOV = stats.get('TOV', 0)
        FGA = stats.get('FGA', 0)
        FTA = stats.get('FTA', 0)
        MP = stats.get('MP', 0)
        
        if MP == 0:
            return 0
        
        # 简化版PER计算（需要联盟平均数据做调整）
        # 实际PER公式更复杂，需要考虑节奏、联盟平均等
        uPER = (
            FG * 2 + TP * 1 + FT * 1 +
            AST * 1.5 + TRB * 1.2 + STL * 2 + BLK * 2 -
            TOV * 1.5 - FGA * 0.8 - FTA * 0.4
        ) / MP * 100
        
        # 调整到基准15
        # 这是一个非常简化的调整
        PER = uPER * 0.15
        
        return round(PER, 2)
    
    def generate_player_analysis(self, player_name: str, player_stats: Dict[str, Any], season: str) -> Dict[str, Any]:
        """
        生成球员高级数据完整分析
        
        Args:
            player_name: 球员姓名
            player_stats: 球员统计数据
            season: 赛季
        
        Returns:
            包含完整分析的字典
        """
        advanced_stats = self.calculate_all_stats(player_stats)
        
        analysis = {
            'player_name': player_name,
            'season': season,
            'basic_stats': player_stats,
            'advanced_stats': advanced_stats,
            'rating_summary': self._rate_player(advanced_stats),
            'strengths': self._find_strengths(advanced_stats),
            'weaknesses': self._find_weaknesses(advanced_stats)
        }
        
        return analysis
    
    def _rate_player(self, stats: Dict[str, float]) -> str:
        """根据PER简单评级"""
        PER = stats.get('PER', 0)
        if PER >= 25:
            return "超级巨星级别"
        elif PER >= 20:
            return "全明星级别"
        elif PER >= 15:
            return "优秀首发级别"
        elif PER >= 10:
            return "合格轮换级别"
        else:
            return "边缘球员级别"
    
    def _find_strengths(self, stats: Dict[str, float]) -> list:
        """找出球员的强项"""
        strengths = []
        
        if stats.get('TS%', 0) > 0.58:
            strengths.append("极高的投篮效率")
        elif stats.get('TS%', 0) > 0.52:
            strengths.append("优秀的投篮效率")
        
        if stats.get('eFG%', 0) > 0.54:
            strengths.append("高效的2分和3分选择")
        
        if stats.get('USG%', 0) > 28:
            strengths.append("高使用率，进攻核心")
        
        if stats.get('AST%', 0) > 25:
            strengths.append("出色的传球组织能力")
        
        if stats.get('STL_per_36', 0) > 1.8:
            strengths.append("优秀的抢断能力")
        
        if stats.get('BLK_per_36', 0) > 1.2:
            strengths.append("出色的盖帽能力")
        
        return strengths
    
    def _find_weaknesses(self, stats: Dict[str, float]) -> list:
        """找出球员的弱项"""
        weaknesses = []
        
        if stats.get('TS%', 0) < 0.48:
            weaknesses.append("投篮效率偏低")
        
        if stats.get('TOV%', 0) > 14:
            weaknesses.append("失误率偏高")
        
        if stats.get('USG%', 0) < 15:
            weaknesses.append("使用率偏低，可能缺乏进攻机会")
        
        if stats.get('AST%', 0) < 10:
            weaknesses.append("传球参与度较低")
        
        return weaknesses


def create_lebron_advanced_stats():
    """创建LeBron的高级统计演示"""
    
    # 示例LeBron数据
    lebron_stats = {
        'GP': 71,  # 场次
        'GS': 71,  # 首发
        'MP': 35.2,  # 分钟
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
        'PTS': 25.0
    }
    
    calculator = AdvancedStatsCalculator()
    analysis = calculator.generate_player_analysis("LeBron James", lebron_stats, "2023-24")
    
    # 保存结果
    with open('nba_data/lebron_analysis/lebron_advanced_stats.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print("✓ LeBron高级统计分析已保存！")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    return analysis


if __name__ == "__main__":
    print("🏀 NBA高级数据计算器")
    print("=" * 50)
    
    # 演示计算LeBron的高级数据
    create_lebron_advanced_stats()
