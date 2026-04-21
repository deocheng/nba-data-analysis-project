# NBA Data Analysis Project

一个用于获取、分析和可视化NBA数据的项目，特别关注球员职业生涯趋势分析。

## 功能特点

- 🔧 **多源数据获取**：整合多个GitHub项目的有效机制
- 📊 **完整数据分析**：球员比赛日志、球队统计、职业生涯数据
- 🎨 **精美可视化**：使用Chart.js创建交互式图表
- 📈 **LeBron James 分析**：专门针对他职业生涯出场时间和休息时间的分析
- 💾 **数据缓存**：避免重复API请求，提高效率

## 参考项目

本项目是在多个优秀的开源NBA项目基础上整合而成的，感谢以下项目的贡献：

### 数据获取与爬取

- **[nba_api](https://github.com/swar/nba_api)** - NBA官方API Python客户端
  - 提供了完整的NBA Stats API封装
  - 支持球员、球队、比赛等多种数据获取

- **[nba_py](https://github.com/seemethere/nba_py)** - 早期的NBA数据获取库
  - 提供了基础的数据获取架构灵感

- **[nba](https://github.com/bttmly/nba)** - 另一个NBA数据获取项目
  - 提供了一些有用的数据处理思路

- **[basketball_reference_web_scraper](https://github.com/jaebradley/basketball_reference_web_scraper)** - Basketball Reference网站数据爬取器
  - 提供了网站数据爬取的完整实现
  - 支持比赛、球员、球队等多维度数据获取

### 数据分析与机器学习

- **[NBA-Machine-Learning-Sports-Betting](https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting)** - NBA机器学习与体育博彩
  - 提供了数据分析和可视化的思路
  - 机器学习应用于NBA分析的示例

- **[nbaStats](https://github.com/nprasad2077/nbaStats)** - NBA统计分析项目
  - 提供了数据统计和分析的方法论
  - 数据处理和可视化的最佳实践

### 项目整合与优化

本项目参考了以上项目的优点，并进行了以下整合和优化：

- ✅ **多数据源整合** - 同时支持NBA API和Basketball Reference
- ✅ **智能缓存机制** - 避免重复API请求，提高效率
- ✅ **统一的架构** - 模块化设计，便于扩展
- ✅ **错误处理** - 完善的异常处理和重试机制
- ✅ **数据可视化** - 丰富的交互式图表和分析页面

## 项目结构

```
nba-data-analysis-project/
├── nba_data/
│   ├── crawler/          # 数据爬取模块
│   │   ├── nba_api_client.py     # NBA API客户端
│   │   ├── bbref_scraper.py      # Basketball Reference爬虫
│   │   └── data_source_selector.py # 数据源选择器
│   ├── processor/        # 数据处理模块  
│   ├── storage/          # 数据存储模块
│   ├── updater/          # 数据更新模块
│   └── lebron_analysis/  # LeBron分析报告
├── cache_manager.py      # 缓存管理
├── data_source_manager.py # 数据源管理
├── enhanced_nba_scraper.py # 增强型数据爬取器
├── analyze_lebron_career.py # LeBron分析脚本
└── collect_all_teams.py # 批量获取球队数据
```

## 核心功能

### 1. NBA 数据爬取
- 使用 nba_api 获取官方数据
- 集成多种数据源（NBA API + Basketball Reference）
- 完善的错误处理和重试机制
- 智能数据缓存系统

### 2. LeBron James 分析
- 职业生涯出场时间趋势
- 最佳出场时长和休息时间计算
- 年龄与出场时间关系分析
- 交互式可视化图表（点状图 + 颜色渐变）

### 3. 数据可视化
- 点状图表展示趋势
- 颜色渐变显示数值大小
- 响应式设计的HTML页面
- 完整的分析报告

### 4. 批量数据处理
- 支持30支球队的完整数据获取
- 多赛季数据管理
- 增量更新机制

## 技术栈

- **后端**：Python 3.x
- **数据处理**：pandas, numpy
- **数据获取**：nba_api
- **可视化**：Chart.js, Matplotlib
- **Web框架**：原生HTML/JavaScript

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动本地服务器
```bash
python -m http.server 8000
```

### 查看分析页面
访问：http://localhost:8000/nba_data/lebron_analysis/

### 运行分析脚本
```bash
# LeBron职业生涯分析
python analyze_lebron_career.py

# 批量获取球队数据
python collect_all_teams.py

# 测试PlayByPlay数据获取
python test_playbyplay_v3.py
```

## 分析特点

这个项目专门研究了LeBron James的职业生涯数据，发现：

- **早期职业生涯（2003-2010）**：高出场时间（近40分钟），低休息时间
- **中期职业生涯（2011-2018）**：逐渐减少出场时间，优化休息策略
- **后期职业生涯（2019-至今）**：显著增加休息时间以延长职业生涯

这个分析模式可以应用于其他球员的职业生涯研究。

## 致谢

感谢所有开源NBA数据项目的贡献者，特别感谢：

- @swar (nba_api)
- @seemethere (nba_py)
- @jaebradley (basketball_reference_web_scraper)
- @kyleskom (NBA-Machine-Learning-Sports-Betting)
- @nprasad2077 (nbaStats)

他们的工作为本项目提供了重要的基础和灵感。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 作者

基于多个开源NBA项目整合而成