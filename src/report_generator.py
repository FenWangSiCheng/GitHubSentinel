from typing import Dict, List, Any
import logging
from datetime import datetime, timezone
from collections import defaultdict
import jinja2
from pathlib import Path
import os

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
        
    def _setup_template_env(self):
        """设置 Jinja2 模板环境"""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        template_loader = jinja2.FileSystemLoader(template_dir)
        return jinja2.Environment(loader=template_loader)
        
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
            grouped_updates: 分组后的更新
            
        Returns:
            str: Markdown格式的报告
        """
        # 打印调试信息
        logger.info("Grouped updates:")
        for section, updates in grouped_updates.items():
            logger.info(f"{section}: {len(updates)} updates")
            if updates:
                logger.info(f"First update in {section}: {updates[0]}")
        
        report = ["# GitHub Repository Updates\n"]
        report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if self.config.get('include_statistics', True):
            report.append("## Statistics\n")
            for type_name, updates in grouped_updates.items():
                report.append(f"- {type_name.title()}: {len(updates)} updates\n")
            report.append("\n")
            
        # 按类型生成详细报告
        for type_name, updates in grouped_updates.items():
            if updates:
                report.append(f"## Recent {type_name.title()}\n")
                
                for update in updates[:10]:  # 最多显示10个更新
                    if type_name == 'commit':
                        report.extend(self._format_commit(update))
                    elif type_name == 'pull_request':
                        report.extend(self._format_pull_request(update))
                    elif type_name == 'issue':
                        report.extend(self._format_issue(update))
                    elif type_name == 'release':
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
            f"### [{commit['title']}]({commit['url']})\n",
            f"**Author:** {commit['author']}  \n",
            f"**Date:** {commit['date'].strftime('%Y-%m-%d %H:%M:%S')}  \n",
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
            f"**Status:** {status}  \n",
            f"**Author:** {pr['author']}  \n",
            f"**Created:** {pr['date'].strftime('%Y-%m-%d %H:%M:%S')}  \n",
            f"**Updated:** {pr['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n",
            f"**Branch:** `{pr['head']}` → `{pr['base']}`\n\n"
        ]
        
    def _format_issue(self, issue: Dict[str, Any]) -> List[str]:
        """格式化议题信息"""
        status = "🟢 Open" if issue['state'] == 'open' else "🔴 Closed"
        labels = ", ".join(f"`{label}`" for label in issue['labels'])
        return [
            f"### [{issue['title']}]({issue['url']})\n",
            f"**Status:** {status}  \n",
            f"**Author:** {issue['author']}  \n",
            f"**Created:** {issue['date'].strftime('%Y-%m-%d %H:%M:%S')}  \n",
            f"**Updated:** {issue['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n",
            f"**Labels:** {labels}\n\n" if labels else "\n"
        ]
        
    def _format_release(self, release: Dict[str, Any]) -> List[str]:
        """格式化发布信息"""
        return [
            f"### [{release['title']}]({release['url']})\n",
            f"**Tag:** {release['tag_name']}  \n",
            f"**Author:** {release['author']}  \n",
            f"**Date:** {release['date'].strftime('%Y-%m-%d %H:%M:%S')}  \n",
            f"**Type:** {'Pre-release' if release['is_prerelease'] else 'Release'}\n\n",
            f"{release['body']}\n\n" if release['body'] else "\n"
        ] 

    def generate_daily_progress_report(self, progress_data: Dict[str, Any]) -> str:
        """
        生成每日进展报告
        
        Args:
            progress_data: 每日进展数据
            
        Returns:
            str: Markdown格式的报告
        """
        report = []
        
        # 添加标题
        report.append(f"# Daily Progress Report - {progress_data['repository']}\n")
        report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"Period: {progress_data['since'].strftime('%Y-%m-%d %H:%M:%S')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 添加统计信息
        report.append("## Statistics\n")
        report.append(f"- Issues: {len(progress_data['issues'])} updates\n")
        report.append(f"- Pull Requests: {len(progress_data['pull_requests'])} updates\n\n")
        
        # 添加Issues详情
        if progress_data['issues']:
            report.append("## Issues\n")
            for issue in progress_data['issues']:
                status = "🟢 Open" if issue['state'] == 'open' else "🔴 Closed"
                report.append(f"### #{issue['number']} - [{issue['title']}]({issue['url']})\n")
                report.append(f"**Status:** {status}  \n")
                report.append(f"**Author:** {issue['author']}  \n")
                report.append(f"**Created:** {issue['created_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report.append(f"**Updated:** {issue['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n")
                if issue['labels']:
                    report.append(f"**Labels:** {', '.join(issue['labels'])}  \n")
                if issue['body']:
                    report.append("\n<details><summary>Description</summary>\n\n")
                    report.append(f"{issue['body']}\n")
                    report.append("</details>\n")
                report.append("\n")
        
        # 添加Pull Requests详情
        if progress_data['pull_requests']:
            report.append("## Pull Requests\n")
            for pr in progress_data['pull_requests']:
                status = "🟢 Merged" if pr['is_merged'] else ("🟡 Open" if pr['state'] == 'open' else "🔴 Closed")
                report.append(f"### #{pr['number']} - [{pr['title']}]({pr['url']})\n")
                report.append(f"**Status:** {status}  \n")
                report.append(f"**Author:** {pr['author']}  \n")
                report.append(f"**Created:** {pr['created_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report.append(f"**Updated:** {pr['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report.append(f"**Branch:** `{pr['head']}` → `{pr['base']}`  \n")
                if pr['body']:
                    report.append("\n<details><summary>Description</summary>\n\n")
                    report.append(f"{pr['body']}\n")
                    report.append("</details>\n")
                report.append("\n")
        
        return "".join(report)

    def save_daily_progress_report(self, progress_data: Dict[str, Any], output_dir: str = "reports") -> str:
        """
        生成并保存每日进展报告
        
        Args:
            progress_data: 每日进展数据
            output_dir: 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        date_str = datetime.now().strftime("%Y-%m-%d")
        repo_name = progress_data['repository'].replace('/', '_')
        filename = f"{repo_name}_progress_{date_str}.md"
        filepath = os.path.join(output_dir, filename)
        
        # 生成报告内容
        content = self.generate_daily_progress_report(progress_data)
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Daily progress report saved to {filepath}")
        return filepath 