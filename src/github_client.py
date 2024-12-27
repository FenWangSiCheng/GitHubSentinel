from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
import logging

from github import Github
from github.Repository import Repository
from github.PaginatedList import PaginatedList
from github.Commit import Commit
from github.Issue import Issue
from github.PullRequest import PullRequest

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, config: Dict[str, str]):
        """
        初始化 GitHub 客户端
        
        Args:
            config: GitHub 配置信息，包含 API token 等
        """
        self.github = Github(config['api_token'])
        self.api_version = config.get('api_version', '2022-11-28')
        self.max_items = 10  # 每种类型最多获取10个更新
        
    async def get_updates(
        self,
        owner: str,
        repo: str,
        track_items: List[str],
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        获取仓库的最新更新
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            track_items: 需要追踪的项目类型列表
            since: 获取此时之后的更新，默认为24小时前
            
        Returns:
            更新列表，每个更新是一个字典
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=1)
        elif since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
            
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            updates = []
            
            for item_type in track_items:
                logger.info(f"Fetching {item_type}...")
                if item_type == "commits":
                    updates.extend(await self._get_commit_updates(repository, since))
                elif item_type == "issues":
                    updates.extend(await self._get_issue_updates(repository, since))
                elif item_type == "pull_requests":
                    updates.extend(await self._get_pr_updates(repository, since))
                elif item_type == "releases":
                    updates.extend(await self._get_release_updates(repository, since))
                logger.info(f"Fetched {item_type}")
                    
            return updates
            
        except Exception as e:
            logger.error(f"Error fetching updates for {owner}/{repo}: {e}")
            raise
            
    async def _get_commit_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取提交更新"""
        try:
            commits = list(repo.get_commits(since=since)[:self.max_items])
            updates = [
                {
                    'type': 'commit',
                    'id': commit.sha,
                    'title': commit.commit.message.split('\n')[0] if commit.commit.message else '',
                    'message': commit.commit.message or '',
                    'author': commit.commit.author.name if commit.commit.author else 'Unknown',
                    'date': commit.commit.author.date if commit.commit.author else datetime.now(timezone.utc),
                    'url': commit.html_url
                }
                for commit in commits
                if commit.commit.author and commit.commit.author.date >= since
            ]
            logger.info(f"Found {len(updates)} new commits")
            return updates
        except Exception as e:
            logger.error(f"Error fetching commits: {e}")
            return []
        
    async def _get_issue_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取议题更新"""
        issues = list(repo.get_issues(state='all', since=since, sort='updated', direction='desc')[:self.max_items])
        updates = [
            {
                'type': 'issue',
                'id': issue.number,
                'title': issue.title,
                'state': issue.state,
                'author': issue.user.login,
                'date': issue.created_at,
                'updated_at': issue.updated_at,
                'url': issue.html_url,
                'labels': [label.name for label in issue.labels]
            }
            for issue in issues
            if issue.updated_at >= since
        ]
        logger.info(f"Found {len(updates)} updated issues")
        return updates
        
    async def _get_pr_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取拉取请求更新"""
        pulls = list(repo.get_pulls(state='all', sort='updated', direction='desc')[:self.max_items])
        updates = [
            {
                'type': 'pull_request',
                'id': pr.number,
                'title': pr.title,
                'state': pr.state,
                'author': pr.user.login,
                'date': pr.created_at,
                'updated_at': pr.updated_at,
                'url': pr.html_url,
                'base': pr.base.ref,
                'head': pr.head.ref,
                'is_merged': pr.merged
            }
            for pr in pulls
            if pr.updated_at >= since
        ]
        logger.info(f"Found {len(updates)} updated pull requests")
        return updates
        
    async def _get_release_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取发布更新"""
        releases = list(repo.get_releases()[:self.max_items])
        updates = [
            {
                'type': 'release',
                'id': release.id,
                'title': release.title or release.tag_name,
                'tag_name': release.tag_name,
                'author': release.author.login,
                'date': release.created_at,
                'url': release.html_url,
                'body': release.body,
                'is_prerelease': release.prerelease
            }
            for release in releases
            if release.created_at >= since
        ]
        logger.info(f"Found {len(updates)} new releases")
        return updates
        
    async def get_daily_progress(
        self,
        owner: str,
        repo: str,
        since: datetime = None
    ) -> Dict[str, Any]:
        """
        获取仓库的每日进展
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            since: 获取此时之后的更新，默认为24小时前
            
        Returns:
            Dict[str, Any]: 包含issues和pull requests的每日进展
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=1)
        elif since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
            
        try:
            logger.info(f"Fetching repository {owner}/{repo}...")
            repository = self.github.get_repo(f"{owner}/{repo}")
            
            # 获取issues列表
            logger.info("Fetching issues...")
            issues = list(repository.get_issues(
                state='all',
                since=since,
                sort='updated',
                direction='desc'
            )[:self.max_items])  # 限制获取数量
            logger.info(f"Found {len(issues)} issues")
            
            # 获取pull requests列表
            logger.info("Fetching pull requests...")
            # 先获取最近更新的PR
            pulls = list(repository.get_pulls(
                state='all',
                sort='updated',
                direction='desc'
            )[:self.max_items])  # 限制获取数量
            logger.info(f"Found {len(pulls)} pull requests")
            
            # 过滤并格式化数据
            logger.info("Processing issues data...")
            formatted_issues = [
                {
                    'number': issue.number,
                    'title': issue.title,
                    'state': issue.state,
                    'author': issue.user.login,
                    'created_at': issue.created_at,
                    'updated_at': issue.updated_at,
                    'url': issue.html_url,
                    'labels': [label.name for label in issue.labels],
                    'body': issue.body
                }
                for issue in issues
                if issue.updated_at >= since
            ]
            logger.info(f"Processed {len(formatted_issues)} issues since {since}")
            
            logger.info("Processing pull requests data...")
            formatted_pulls = [
                {
                    'number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'author': pr.user.login,
                    'created_at': pr.created_at,
                    'updated_at': pr.updated_at,
                    'url': pr.html_url,
                    'base': pr.base.ref,
                    'head': pr.head.ref,
                    'is_merged': pr.merged,
                    'body': pr.body
                }
                for pr in pulls
                if pr.updated_at >= since
            ]
            logger.info(f"Processed {len(formatted_pulls)} pull requests since {since}")
            
            return {
                'repository': f"{owner}/{repo}",
                'since': since,
                'issues': formatted_issues,
                'pull_requests': formatted_pulls
            }
            
        except Exception as e:
            logger.error(f"Error fetching daily progress for {owner}/{repo}: {e}")
            raise
        
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'github'):
            self.github.close() 