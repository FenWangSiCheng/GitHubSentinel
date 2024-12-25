from typing import Dict, List, Any
import logging
from datetime import datetime
from collections import defaultdict
import jinja2
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化报告生成器
        
        Args:
            config: 报告配置信息
        """
        self.config = config
        self.template_env = self._setup_template_env()
        
    def _setup_template_env(self) -> jinja2.Environment:
        """设置Jinja2模板环境"""
        template_loader = jinja2.PackageLoader('github_sentinel', 'templates')
        env = jinja2.Environment(
            loader=template_loader,
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 添加自定义过滤器
        env.filters['format_date'] = lambda d: d.strftime('%Y-%m-%d %H:%M:%S')
        return env
        
    def generate_report(self, updates: List[Dict[str, Any]]) -> str:
        """
        生成更新报告
        
        Args:
            updates: 更新列表
            
        Returns:
            str: 生成的报告内容
        """
        # 按类型分组更新
        grouped_updates = self._group_updates(updates)
        
        # 生成报告内容
        if self.config.get('format', 'markdown') == 'markdown':
            return self._generate_markdown_report(grouped_updates)
        else:
            return self._generate_html_report(grouped_updates)
            
    def _group_updates(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        将更新按类型分组
        
        Args:
            updates: 更新列表
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 分组后的更新
        """
        grouped = defaultdict(list)
        for update in updates:
            grouped[update['type']].append(update)
            
        # 按时间排序
        for updates_list in grouped.values():
            updates_list.sort(key=lambda x: x['date'], reverse=True)
            
        return grouped
        
    def _generate_markdown_report(
        self,
        grouped_updates: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """
        生成Markdown格式的报告
        
        Args:
            grouped_updates: 分组后的���新
            
        Returns:
            str: Markdown格式的报告
        """
        sections = self.config.get('sections', ['commits', 'pull_requests', 'issues', 'releases'])
        max_items = self.config.get('max_items_per_section', 10)
        
        report = ["# GitHub Repository Updates\n"]
        report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if self.config.get('include_statistics', True):
            report.append("## Statistics\n")
            for type_name, updates in grouped_updates.items():
                report.append(f"- {type_name.title()}: {len(updates)} updates\n")
            report.append("\n")
            
        for section in sections:
            if section in grouped_updates:
                updates = grouped_updates[section][:max_items]
                report.append(f"## {section.title()}\n")
                
                for update in updates:
                    if section == 'commits':
                        report.extend(self._format_commit(update))
                    elif section == 'pull_requests':
                        report.extend(self._format_pull_request(update))
                    elif section == 'issues':
                        report.extend(self._format_issue(update))
                    elif section == 'releases':
                        report.extend(self._format_release(update))
                        
                report.append("\n")
                
        return "\n".join(report)
        
    def _generate_html_report(
        self,
        grouped_updates: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """
        生成HTML格式的报告
        
        Args:
            grouped_updates: 分组后的更新
            
        Returns:
            str: HTML格式的报告
        """
        template = self.template_env.get_template('report.html')
        return template.render(
            updates=grouped_updates,
            config=self.config,
            generated_at=datetime.now()
        )
        
    def _format_commit(self, commit: Dict[str, Any]) -> List[str]:
        """格式化提交信息"""
        return [
            f"### {commit['title']}\n",
            f"**Author:** {commit['author']}  ",
            f"**Date:** {commit['date'].strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Hash:** [{commit['id'][:7]}]({commit['url']})\n",
            f"```\n{commit['message']}\n```\n"
        ]
        
    def _format_pull_request(self, pr: Dict[str, Any]) -> List[str]:
        """格式化拉取请求信息"""
        status = "🟢 Merged" if pr['is_merged'] else (
            "🟡 Open" if pr['state'] == 'open' else "🔴 Closed"
        )
        return [
            f"### [{pr['title']}]({pr['url']})\n",
            f"**Status:** {status}  ",
            f"**Author:** {pr['author']}  ",
            f"**Created:** {pr['date'].strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Updated:** {pr['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Branch:** `{pr['head']}` → `{pr['base']}`\n"
        ]
        
    def _format_issue(self, issue: Dict[str, Any]) -> List[str]:
        """格式化议题信息"""
        status = "🟢 Open" if issue['state'] == 'open' else "🔴 Closed"
        labels = ", ".join(f"`{label}`" for label in issue['labels'])
        return [
            f"### [{issue['title']}]({issue['url']})\n",
            f"**Status:** {status}  ",
            f"**Author:** {issue['author']}  ",
            f"**Created:** {issue['date'].strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Updated:** {issue['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Labels:** {labels}\n" if labels else "\n"
        ]
        
    def _format_release(self, release: Dict[str, Any]) -> List[str]:
        """格式化发布信息"""
        return [
            f"### [{release['title']}]({release['url']})\n",
            f"**Tag:** {release['tag_name']}  ",
            f"**Author:** {release['author']}  ",
            f"**Date:** {release['date'].strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Type:** {'Pre-release' if release['is_prerelease'] else 'Release'}\n",
            f"{release['body']}\n" if release['body'] else "\n"
        ] 