# GitHub Sentinel

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub API](https://img.shields.io/badge/GitHub-API%20v3-green.svg)](https://docs.github.com/en/rest)

GitHub Sentinel is an intelligent GitHub repository monitoring tool that automatically tracks and summarizes updates from your favorite open source projects. Whether it's code changes, issue discussions, or version releases, GitHub Sentinel provides timely and accurate information aggregation, ensuring you never miss important updates.

## ✨ Features

- 🔄 **Smart Tracking**: Automatically monitor repository commits, issues, pull requests, and releases
- 📊 **Data Aggregation**: Intelligently aggregate updates from multiple repositories and generate clear statistical reports
- 🔔 **Multi-channel Notifications**: Support for email, Slack, and other notification methods to ensure timely updates
- 📝 **Flexible Reporting**: Support for both Markdown and HTML format reports
- 🎯 **Precise Subscriptions**: Configure different tracking items for different repositories
- 💾 **History Records**: Local storage of update history with query and statistical analysis support

## 🚀 Use Cases

- Open source project maintainers tracking dependency updates
- Teams monitoring related project progress
- Tech enthusiasts following interesting open source projects
- Project managers collecting and analyzing project activity data

## 🛠 Technical Architecture

- Python 3.8+ environment
- GitHub API v3 integration
- SQLite/PostgreSQL data persistence
- Asynchronous processing and scheduled tasks
- Modular design for easy extension

## 📦 Quick Start

1. Clone the repository
```bash
git clone https://github.com/yourusername/github-sentinel.git
cd github-sentinel
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure
- Copy `config/config.example.yaml` to `config/config.yaml`
- Set up your GitHub API token and other configurations

4. Run
```bash
python src/main.py
```

## ⚙️ Configuration

The configuration file is located at `config/config.yaml` and includes:
- GitHub API configuration (token, API version, etc.)
- Repository subscription list and tracking items
- Notification settings (email, Slack)
- Update check frequency and report format

## 📊 Report Examples

### Markdown Format
```markdown
# GitHub Repository Updates
Generated at: 2024-01-20 10:00:00

## Statistics
- Commits: 12 updates
- Pull Requests: 5 updates
- Issues: 8 updates
- Releases: 1 update
```

### HTML Format
- Beautiful web interface
- Interactive statistics charts
- Responsive design for mobile devices

## 🤝 Contributing

Contributions are welcome! Please check out our [CONTRIBUTING.md](CONTRIBUTING.md) to learn how to participate in the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 