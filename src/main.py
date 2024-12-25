#!/usr/bin/env python3
import os
import logging
import schedule
import time
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

from github_client import GitHubClient
from subscription_manager import SubscriptionManager
from update_tracker import UpdateTracker
from notification_service import NotificationService
from report_generator import ReportGenerator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                repo_updates = await self.github_client.get_updates(
                    owner=repo['owner'],
                    repo=repo['repo'],
                    track_items=repo['track']
                )
                updates.extend(repo_updates)
            
            # 过滤出新的更新
            new_updates = self.update_tracker.filter_new_updates(updates)
            
            if new_updates:
                # 生成报告
                report = self.report_generator.generate_report(new_updates)
                
                # 发送通知
                await self.notification_service.send_notifications(report)
                
                # 标记更新为已处理
                self.update_tracker.mark_as_processed(new_updates)
                
            logger.info(f"Update check completed. Found {len(new_updates)} new updates.")
            
        except Exception as e:
            logger.error(f"Error during update check: {e}")
            await self.notification_service.send_error_notification(str(e))

    def schedule_jobs(self):
        """设置定时任务"""
        interval = self.config['subscriptions']['update_interval']
        check_time = self.config['subscriptions']['check_time']
        
        if interval == 'daily':
            schedule.every().day.at(check_time).do(self.check_updates)
        elif interval == 'weekly':
            schedule.every().monday.at(check_time).do(self.check_updates)
        
        logger.info(f"Scheduled update checks for {interval} at {check_time}")

    def run(self):
        """运行主程序"""
        logger.info("Starting GitHub Sentinel...")
        self.schedule_jobs()
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    # 加载环境变量
    load_dotenv()
    
    # 获取配置文件路径
    config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
    
    # 创建并运行 Sentinel
    sentinel = GitHubSentinel(config_path)
    sentinel.run()

if __name__ == '__main__':
    main() 