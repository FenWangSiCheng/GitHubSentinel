# GitHub Sentinel

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub API](https://img.shields.io/badge/GitHub-API%20v3-green.svg)](https://docs.github.com/en/rest)

GitHub Sentinel 是一款智能化的 GitHub 仓库监控工具，它能够自动追踪和汇总你关注的开源项目的最新动态。无论是代码更新、问题讨论，还是版本发布，GitHub Sentinel 都能及时为你提供精准的信息聚合，让你不错过任何重要更新。

## ✨ 特性亮点

- 🔄 **智能追踪**：自动监控仓库的 commits、issues、pull requests 和 releases
- 📊 **数据聚合**：智能汇总多个仓库的更新，生成清晰的统计报告
- 🔔 **多渠道通知**：支持邮件、Slack 等多种通知方式，确保及时获取更新
- 📝 **灵活报告**：支持 Markdown 和 HTML 两种格式的精美报告
- 🎯 **精准订阅**：可针对不同仓库设置不同的追踪项目
- 💾 **历史记录**：本地存储更新历史，支持查询和统计分析

## 🚀 应用场景

- 开源项目维护者追踪依赖库的更新
- 团队协作中监控相关项目的进展
- 技术爱好者追踪感兴趣的开源项目
- 项目经理统计和分析项目活动数据

## 🛠 技术架构

- Python 3.8+ 环境支持
- GitHub API v3 接口集成
- SQLite/PostgreSQL 数据持久化
- 异步处理和定时任务调度
- 模块化设计，易于扩展

## 📦 快速开始

1. 克隆仓库
```bash
git clone https://github.com/yourusername/github-sentinel.git
cd github-sentinel
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置
- 复制 `config/config.example.yaml` 到 `config/config.yaml`
- 设置你的 GitHub API token 和其他配置

4. 运行
```bash
python src/main.py
```

## ⚙️ 配置说明

配置文件位于 `config/config.yaml`，主要包含：
- GitHub API 配置（token、API 版本等）
- 订阅仓库列表及追踪项目
- 通知设置（邮件、Slack）
- 更新检查频率和报告格式

## 📊 报告示例

### Markdown 格式
```markdown
# GitHub Repository Updates
Generated at: 2024-01-20 10:00:00

## Statistics
- Commits: 12 updates
- Pull Requests: 5 updates
- Issues: 8 updates
- Releases: 1 update
```

### HTML 格式
- 美观的 Web 界面
- 交互式统计图表
- 响应式设计，支持移动端

## 🤝 贡献指南

欢迎贡献代码或提出建议！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。 