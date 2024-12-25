# Release Notes

## v0.1 - Initial Release (2024-12-25)

First release of GitHub Sentinel, an interactive tool for monitoring GitHub repository updates.

### Features

- **Interactive Shell**: A command-line interface with interactive shell for better user experience
- **Real-time Monitoring**: Watch GitHub repositories for updates in real-time
- **Flexible Configuration**: Easy configuration management through interactive commands
- **Repository Management**: Add/remove repositories to monitor with customizable tracking items
- **Comprehensive Updates**: Track multiple types of updates:
  - Commits
  - Pull Requests
  - Issues
  - Releases
- **Scheduled Checks**: Configurable scheduled checks (daily/weekly) at specified times
- **Immediate Updates**: On-demand update checks
- **Detailed Reports**: Well-formatted reports in Markdown format
- **Background Service**: Watch service runs in background while keeping shell interactive

### Commands

- `check` - Check updates immediately
- `watch` - Start watch service in background
- `stop` - Stop watch service
- `config`
  - `config list` - List current configuration
  - `config set <key> <value>` - Update configuration
- `repo`
  - `repo list` - List monitored repositories
  - `repo add <owner> <repo> [--track items...]` - Add repository to monitor
  - `repo remove <owner> <repo>` - Remove repository from monitoring
- `status` - Show current system status
- `exit` - Exit the program (also supports Ctrl-D)

### Technical Details

- Built with Python 3.8+
- Uses GitHub API v3
- Asynchronous operations for better performance
- Local SQLite database for update tracking
- YAML-based configuration
- Modular architecture for easy extension 