from typing import Dict, List, Any
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class SubscriptionManager:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化订阅管理器
        
        Args:
            config: 订阅配置信息
        """
        self.config = config
        self._subscriptions = self._load_subscriptions()
        
    def _load_subscriptions(self) -> List[Dict[str, Any]]:
        """从配置中加载订阅信息"""
        return self.config.get('repositories', [])
        
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """获取所有订阅的仓库信息"""
        return self._subscriptions
        
    def add_subscription(
        self,
        owner: str,
        repo: str,
        track_items: List[str] = None
    ) -> bool:
        """
        添加新的仓库订阅
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            track_items: 需要追踪的项目类型列表，默认为 ['commits', 'issues']
            
        Returns:
            bool: 是否添加成功
        """
        if track_items is None:
            track_items = ['commits', 'issues']
            
        # 检查是否已存在
        for sub in self._subscriptions:
            if sub['owner'] == owner and sub['repo'] == repo:
                logger.warning(f"Repository {owner}/{repo} already subscribed")
                return False
                
        # 添加新订阅
        new_sub = {
            'owner': owner,
            'repo': repo,
            'track': track_items
        }
        self._subscriptions.append(new_sub)
        self._save_subscriptions()
        
        logger.info(f"Added subscription for {owner}/{repo}")
        return True
        
    def remove_subscription(self, owner: str, repo: str) -> bool:
        """
        移除仓库订阅
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            bool: 是否移除成功
        """
        initial_count = len(self._subscriptions)
        self._subscriptions = [
            sub for sub in self._subscriptions
            if not (sub['owner'] == owner and sub['repo'] == repo)
        ]
        
        if len(self._subscriptions) < initial_count:
            self._save_subscriptions()
            logger.info(f"Removed subscription for {owner}/{repo}")
            return True
            
        logger.warning(f"Repository {owner}/{repo} not found in subscriptions")
        return False
        
    def update_subscription(
        self,
        owner: str,
        repo: str,
        track_items: List[str]
    ) -> bool:
        """
        更新仓库订阅的追踪项
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            track_items: 新的追踪项列表
            
        Returns:
            bool: 是否更新成功
        """
        for sub in self._subscriptions:
            if sub['owner'] == owner and sub['repo'] == repo:
                sub['track'] = track_items
                self._save_subscriptions()
                logger.info(f"Updated subscription for {owner}/{repo}")
                return True
                
        logger.warning(f"Repository {owner}/{repo} not found in subscriptions")
        return False
        
    def _save_subscriptions(self):
        """保存订阅信息到配置"""
        self.config['repositories'] = self._subscriptions
        
    def get_subscription(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        获取特定仓库的订阅信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            Dict[str, Any]: 订阅信息，如果不存在返回 None
        """
        for sub in self._subscriptions:
            if sub['owner'] == owner and sub['repo'] == repo:
                return sub
        return None
        
    def list_subscriptions(self) -> List[str]:
        """
        获取所有订阅仓库的列表
        
        Returns:
            List[str]: 仓库列表，格式为 "owner/repo"
        """
        return [f"{sub['owner']}/{sub['repo']}" for sub in self._subscriptions] 