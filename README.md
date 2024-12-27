# GitHub Sentinel

GitHub Sentinel is an intelligent GitHub repository monitoring tool that helps you track repository updates, generate reports, and provides AI-driven analysis.

## Features

- 🔍 Smart Repository Tracking
  - Commits
  - Issues
  - Pull Requests
  - Releases
- 📊 Data Aggregation & Analysis
  - Automatic Daily Progress Reports
  - AI-Powered Report Summaries and Analysis
- 📱 Multi-Channel Notifications
  - Email Notifications
  - Slack Integration
- 📝 Flexible Report Formats
  - Markdown
  - HTML

## Technical Architecture

- Python 3.8+
- GitHub API v3
- OpenAI GPT API
- SQLite/PostgreSQL

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/github-sentinel.git
cd github-sentinel
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the project:
   - Copy the example configuration file:
     ```bash
     cp config/config.example.yaml config/config.yaml
     ```
   - Edit `config/config.yaml` to set:
     - GitHub API token
     - OpenAI API key (for AI report generation)
     - Repository list to monitor
     - Notification settings

5. Run the project:
```bash
python src/main.py
```

## Configuration Guide

### GitHub Configuration
```yaml
github:
  api_token: "your-github-token"
  api_version: "2022-11-28"
```

### LLM Configuration (for AI Report Generation)
```yaml
llm:
  type: "openai"
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-3.5-turbo"
```

### Database Configuration
```yaml
database:
  type: "sqlite"  # or "postgresql"
  path: "data/sentinel.db"  # sqlite path
  # postgresql_url: "postgresql://user:password@localhost:5432/dbname"
```

### Subscription Settings
```yaml
subscriptions:
  update_interval: "daily"  # or "weekly"
  check_time: "09:00"
  repositories:
    - owner: "owner-name"
      repo: "repo-name"
      track:
        - "commits"
        - "issues"
        - "pull_requests"
        - "releases"
```

## Usage Guide

Available commands in the interactive shell:

- `help` - Display help information
- `check` - Check updates immediately
- `watch` - Start background monitoring service
- `stop` - Stop monitoring service
- `progress [owner/repo]` - Generate repository progress report
- `summarize` - Generate AI summary report
- `status` - Show current status
- `config` - Configuration management
- `repo` - Repository management
- `exit` - Exit program

## Report Examples

### Daily Progress Report
```markdown
# Daily Progress Report - 2024-01-01
Repository: owner/repo

## Statistics
- New Commits: 5
- Updated Issues: 3
- Updated Pull Requests: 2

## Details
...
```

### AI Summary Report
```markdown
# Project Daily Summary - 2024-01-01
Repository: owner/repo

## Overview
[AI-generated project overview]

## Key Updates
[Important update summary]

## Analysis & Recommendations
[AI analysis and suggestions]
```

## License

[MIT License](LICENSE) 