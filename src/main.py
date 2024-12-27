#!/usr/bin/env python3
import os
import logging
import schedule
import time
import asyncio
import argparse
import cmd
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from dotenv import load_dotenv

from github_client import GitHubClient
from subscription_manager import SubscriptionManager
from update_tracker import UpdateTracker
from notification_service import NotificationService
from report_generator import ReportGenerator
from report_generator_ai import AIReportGenerator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubSentinelShell(cmd.Cmd):
    intro = 'Welcome to GitHub Sentinel shell. Type help or ? to list commands.\n'
    prompt = '(sentinel) '
    
    def __init__(self, sentinel: 'GitHubSentinel'):
        super().__init__()
        self.sentinel = sentinel
        self._watch_task = None
        
    def do_check(self, arg):
        """Check updates immediately"""
        asyncio.run(self.sentinel.check_updates())
        
    def do_watch(self, arg):
        """Start watch service in background"""
        if self._watch_task and not self._watch_task.done():
            print("Watch service is already running")
            return
            
        self._watch_task = asyncio.create_task(self._watch_service())
        print("Watch service started")
        
    def do_stop(self, arg):
        """Stop watch service"""
        if self._watch_task and not self._watch_task.done():
            self._watch_task.cancel()
            print("Watch service stopped")
        else:
            print("Watch service is not running")
            
    def do_config(self, arg):
        """Configuration management
        Usage:
            config list
            config set <key> <value>
        """
        args = shlex.split(arg)
        if not args:
            print("Error: Missing subcommand. Use 'help config' for usage.")
            return
            
        if args[0] == 'list':
            self.sentinel.config_list()
        elif args[0] == 'set' and len(args) == 3:
            self.sentinel.config_set(args[1], args[2])
        else:
            print("Error: Invalid command. Use 'help config' for usage.")
            
    def do_repo(self, arg):
        """Repository management
        Usage:
            repo list
            repo add <owner> <repo> [--track items...]
            repo remove <owner> <repo>
        """
        args = shlex.split(arg)
        if not args:
            print("Error: Missing subcommand. Use 'help repo' for usage.")
            return
            
        if args[0] == 'list':
            self.sentinel.repo_list()
        elif args[0] == 'add' and len(args) >= 3:
            owner = args[1]
            repo = args[2]
            track_items = args[4:] if len(args) > 4 and args[3] == '--track' else \
                         ['commits', 'issues', 'pull_requests', 'releases']
            self.sentinel.repo_add(owner, repo, track_items)
        elif args[0] == 'remove' and len(args) == 3:
            self.sentinel.repo_remove(args[1], args[2])
        else:
            print("Error: Invalid command. Use 'help repo' for usage.")
            
    def do_status(self, arg):
        """Show current status"""
        print("\nGitHub Sentinel Status:")
        print(f"Watch Service: {'Running' if self._watch_task and not self._watch_task.done() else 'Stopped'}")
        print("\nMonitored Repositories:")
        self.sentinel.repo_list()
            
    def do_exit(self, arg):
        """Exit GitHub Sentinel"""
        if self._watch_task and not self._watch_task.done():
            self._watch_task.cancel()
        print("\nGoodbye!")
        return True
        
    def do_EOF(self, arg):
        """Exit on Ctrl-D"""
        return self.do_exit(arg)
        
    def do_progress(self, arg):
        """Generate daily progress report for repositories
        Usage:
            progress [owner/repo]  # Generate report for specific repository
            progress              # Generate reports for all subscribed repositories
        """
        args = shlex.split(arg)
        
        async def generate_progress():
            try:
                if args:
                    # 处理单个仓库
                    repo_path = args[0]
                    try:
                        owner, repo = repo_path.split('/')
                    except ValueError:
                        print("Error: Repository should be in format 'owner/repo'")
                        return
                        
                    print(f"\nGenerating progress report for {owner}/{repo}...")
                    # 获取进展数据
                    progress_data = await self.sentinel.github_client.get_daily_progress(owner, repo)
                    
                    print("Generating report...")
                    # 生成并保存报告
                    filepath = self.sentinel.report_generator.save_daily_progress_report(progress_data)
                    print(f"Daily progress report generated: {filepath}")
                    
                else:
                    # 处理所有订阅的仓库
                    repositories = self.sentinel.subscription_manager.get_subscriptions()
                    print(f"\nGenerating progress reports for {len(repositories)} repositories...")
                    
                    for repo_info in repositories:
                        print(f"\nProcessing {repo_info['owner']}/{repo_info['repo']}...")
                        progress_data = await self.sentinel.github_client.get_daily_progress(
                            repo_info['owner'],
                            repo_info['repo']
                        )
                        print("Generating report...")
                        filepath = self.sentinel.report_generator.save_daily_progress_report(progress_data)
                        print(f"Report generated: {filepath}")
                        
            except Exception as e:
                print(f"Error generating progress report: {e}")
                logger.error(f"Error generating progress report: {e}")
                
        asyncio.run(generate_progress())
        
    def do_summarize(self, arg):
        """Generate AI summary reports for today's progress reports
        Usage:
            summarize  # Generate summary reports for all today's progress reports
        """
        async def generate_summaries():
            try:
                print("\nGenerating AI summary reports...")
                await self.sentinel.ai_report_generator.process_daily_reports()
                print("Summary reports generated successfully.")
                
            except Exception as e:
                print(f"Error generating summary reports: {e}")
                logger.error(f"Error generating summary reports: {e}")
                
        asyncio.run(generate_summaries())
        
    async def _watch_service(self):
        """Watch service implementation"""
        try:
            logger.info("Starting watch service...")
            self.sentinel.schedule_jobs()
            
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Watch service stopped")
        except Exception as e:
            logger.error(f"Watch service error: {e}")

class GitHubSentinel:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # 初始化各个组件
        self.github_client = GitHubClient(self.config['github'])
        self.subscription_manager = SubscriptionManager(self.config['subscriptions'])
        self.update_tracker = UpdateTracker(self.config['database'])
        self.notification_service = NotificationService(self.config['notifications'])
        self.report_generator = ReportGenerator(self.config['reports'])
        self.ai_report_generator = AIReportGenerator(self.config)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _setup_logging(self):
        """配置日志系统"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file', 'logs/sentinel.log')
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        logger.setLevel(log_config.get('level', 'INFO'))

    async def check_updates(self):
        """检查所有订阅仓库的更新"""
        try:
            # 获取所有订阅的仓库
            repositories = self.subscription_manager.get_subscriptions()
            
            # 获取每个仓库的更新
            updates = []
            for repo in repositories:
                logger.info(f"Checking updates for {repo['owner']}/{repo['repo']}...")
                repo_updates = await self.github_client.get_updates(
                    owner=repo['owner'],
                    repo=repo['repo'],
                    track_items=repo['track']
                )
                updates.extend(repo_updates)
                logger.info(f"Found {len(repo_updates)} updates")
            
            # 生成报告（无论是否有新更新）
            report = self.report_generator.generate_report(updates)
            
            # 打印报告内容
            print("\n=== Generated Report ===\n")
            print(report)
            print("\n=== End of Report ===\n")
            
            logger.info(f"Update check completed. Found {len(updates)} updates total.")
            
        except Exception as e:
            logger.error(f"Error during update check: {e}")
            await self.notification_service.send_error_notification(str(e))

    def watch(self):
        """启动监控服务"""
        logger.info("Starting GitHub Sentinel watch service...")
        self.schedule_jobs()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Watch service stopped by user")

    def schedule_jobs(self):
        """设置定时任务"""
        interval = self.config['subscriptions']['update_interval']
        check_time = self.config['subscriptions']['check_time']
        
        if interval == 'daily':
            schedule.every().day.at(check_time).do(self.check_updates)
        elif interval == 'weekly':
            schedule.every().monday.at(check_time).do(self.check_updates)
        
        logger.info(f"Scheduled update checks for {interval} at {check_time}")

    def config_list(self):
        """列出当前配置"""
        print("\nCurrent Configuration:")
        print(yaml.dump(self.config, default_flow_style=False))

    def config_set(self, key: str, value: str):
        """设置配置项"""
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        # 保存配置
        config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        print(f"Configuration updated: {key} = {value}")

    def repo_list(self):
        """列出所有监控的仓库"""
        repos = self.subscription_manager.get_subscriptions()
        print("\nMonitored Repositories:")
        for repo in repos:
            print(f"- {repo['owner']}/{repo['repo']}")
            print(f"  Tracking: {', '.join(repo['track'])}")

    def repo_add(self, owner: str, repo: str, track_items: List[str]):
        """添加监控仓库"""
        repos = self.subscription_manager.get_subscriptions()
        repos.append({
            'owner': owner,
            'repo': repo,
            'track': track_items
        })
        
        # 更新配置
        self.config['subscriptions']['repositories'] = repos
        config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        print(f"Added repository: {owner}/{repo}")

    def repo_remove(self, owner: str, repo: str):
        """移除监控仓库"""
        repos = self.subscription_manager.get_subscriptions()
        repos = [r for r in repos if not (r['owner'] == owner and r['repo'] == repo)]
        
        # 更新配置
        self.config['subscriptions']['repositories'] = repos
        config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        print(f"Removed repository: {owner}/{repo}")

def main():
    # 加载环境变量
    load_dotenv()
    
    # 获取配置文件路径
    config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
    
    # 创建 Sentinel 实例
    sentinel = GitHubSentinel(config_path)
    
    # 创建并启动交互式 shell
    shell = GitHubSentinelShell(sentinel)
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == '__main__':
    main() 