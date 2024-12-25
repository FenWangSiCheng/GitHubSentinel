from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from github import Github
from github.Repository import Repository
from github.PaginatedList import PaginatedList
from github.Commit import Commit
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Release import Release

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
            since: 获取此时���之后的更新，默认为24小时前
            
        Returns:
            更新列表，每个更新是一个字典
        """
        if since is None:
            since = datetime.now() - timedelta(days=1)
            
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            updates = []
            
            for item_type in track_items:
                if item_type == "commits":
                    updates.extend(await self._get_commit_updates(repository, since))
                elif item_type == "issues":
                    updates.extend(await self._get_issue_updates(repository, since))
                elif item_type == "pull_requests":
                    updates.extend(await self._get_pr_updates(repository, since))
                elif item_type == "releases":
                    updates.extend(await self._get_release_updates(repository, since))
                    
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
        commits = repo.get_commits(since=since)
        return [
            {
                'type': 'commit',
                'id': commit.sha,
                'title': commit.commit.message.split('\n')[0],
                'message': commit.commit.message,
                'author': commit.commit.author.name,
                'date': commit.commit.author.date,
                'url': commit.html_url
            }
            for commit in commits
        ]
        
    async def _get_issue_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取议题更新"""
        issues = repo.get_issues(state='all', since=since)
        return [
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
        ]
        
    async def _get_pr_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取拉取请求更新"""
        pulls = repo.get_pulls(state='all', sort='updated', direction='desc')
        return [
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
        
    async def _get_release_updates(
        self,
        repo: Repository,
        since: datetime
    ) -> List[Dict[str, Any]]:
        """获取发布更新"""
        releases = repo.get_releases()
        return [
            {
                'type': 'release',
                'id': release.id,
                'title': release.title,
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
        
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'github'):
            self.github.close() 