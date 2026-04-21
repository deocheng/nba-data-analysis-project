# NBA Data Analysis Project

一个用于获取、分析和可视化NBA数据的项目，特别关注球员职业生涯趋势分析。

## 功能特点

- 🔧 **多源数据获取**：整合多个GitHub项目的有效机制
- 📊 **完整数据分析**：球员比赛日志、球队统计、职业生涯数据
- 🎨 **精美可视化**：使用Chart.js创建交互式图表
- 📈 **LeBron James 分析**：专门针对他职业生涯出场时间和休息时间的分析
- 💾 **数据缓存**：避免重复API请求，提高效率

## 项目结构

```
AutoPick/
├── nba_data/
│   ├── crawler/          # 数据爬取模块
│   ├── processor/        # 数据处理模块  
│   ├── storage/          # 数据存储模块
│   └── lebron_analysis/  # LeBron分析报告
├── cache_manager.py      # 缓存管理
└── data_source_manager.py # 数据源管理
```

## 核心功能

### 1. NBA 数据爬取
- 使用 nba_api 获取官方数据
- 集成多种数据源
- 错误处理和重试机制

### 2. LeBron James 分析
- 职业生涯出场时间趋势
- 最佳出场时长和休息时间计算
- 年龄与出场时间关系分析
- 交互式可视化图表

### 3. 数据可视化
- 点状图表展示趋势
- 颜色渐变显示数值大小
- 响应式设计

## 技术栈

- **后端**：Python 3.x
- **数据处理**：pandas, numpy
- **数据获取**：nba_api
- **可视化**：Chart.js
- **Web框架**：原生HTML/JavaScript

## 使用方法

### 启动本地服务器
```bash
python -m http.server 8000
```

### 查看分析页面
访问：http://localhost:8000/nba_data/lebron_analysis/

## 分析特点

这个项目专门研究了LeBron James的职业生涯数据，发现：

- 早期职业生涯：高出场时间，低休息时间
- 中期职业生涯：逐渐减少出场时间
- 后期职业生涯：显著增加休息时间以延长职业生涯

## 许可证

MIT License

## 作者

基于多个开源NBA项目整合而成