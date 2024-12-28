import os
import gradio as gr
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from main import GitHubSentinel

logger = logging.getLogger(__name__)

class WebInterface:
    def __init__(self, sentinel: GitHubSentinel):
        self.sentinel = sentinel
        self.is_watching = False
        self._watch_task = None
        
    def create_interface(self):
        """Create and configure the Gradio interface"""
        with gr.Blocks(title="GitHub Sentinel", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# GitHub Sentinel")
            gr.Markdown("Monitor and analyze GitHub repository updates with AI-powered insights")
            
            with gr.Tabs():
                # Dashboard Tab
                with gr.Tab("Dashboard"):
                    with gr.Row():
                        with gr.Column():
                            watch_button = gr.Button("Start Watching", variant="primary")
                            stop_button = gr.Button("Stop Watching", variant="secondary")
                        status_text = gr.Textbox(label="Status", value="Stopped", interactive=False)
                    
                    check_button = gr.Button("Check Updates Now")
                    report_output = gr.Markdown()
                    
                # Repository Management Tab
                with gr.Tab("Repositories"):
                    # 获取初始仓库列表
                    initial_repos = self.sentinel.subscription_manager.get_subscriptions()
                    initial_repo_data = [[repo['owner'], repo['repo'], ', '.join(repo['track'])] for repo in initial_repos]
                    initial_choices = [f"{repo['owner']}/{repo['repo']}" for repo in initial_repos]
                    
                    with gr.Row():
                        with gr.Column():
                            repo_input = gr.Dropdown(
                                label="Repository",
                                choices=initial_choices,
                                allow_custom_value=True,
                                value="",
                                info="Select a repository or enter a new one (format: owner/repo)"
                            )
                            track_input = gr.CheckboxGroup(
                                choices=["commits", "issues", "pull_requests", "releases"],
                                value=["commits", "issues", "pull_requests", "releases"],
                                label="Track Items"
                            )
                            with gr.Row():
                                add_repo_button = gr.Button("Add Repository", variant="primary")
                                remove_repo_button = gr.Button("Remove Repository", variant="secondary")
                        with gr.Column():
                            repo_list = gr.Dataframe(
                                headers=["Owner", "Repository", "Tracking"],
                                label="Monitored Repositories",
                                interactive=False,
                                wrap=True,
                                value=initial_repo_data  # 设置初始值
                            )
                            refresh_repos_button = gr.Button("Refresh List")
                            status_message = gr.Textbox(
                                label="Status",
                                interactive=False
                            )
                            
                # Reports Tab
                with gr.Tab("Reports"):
                    with gr.Row():
                        with gr.Column():
                            report_type = gr.Radio(
                                choices=["Progress Report", "AI Summary"],
                                label="Report Type",
                                value="Progress Report",
                                interactive=True
                            )
                            repo_select = gr.Dropdown(
                                label="Repository",
                                choices=initial_choices,
                                allow_custom_value=True,
                                info="Select a repository to generate report"
                            )
                        generate_report_button = gr.Button("Generate Report", variant="primary")
                    report_view = gr.Markdown()
                    
                # Configuration Tab
                with gr.Tab("Configuration"):
                    config_text = gr.TextArea(
                        label="Configuration (YAML)",
                        interactive=True,
                        lines=20
                    )
                    with gr.Row():
                        save_config_button = gr.Button("Save Configuration", variant="primary")
                        reload_config_button = gr.Button("Reload", variant="secondary")
                    config_status = gr.Textbox(label="Status", interactive=False)
            
            # Event handlers
            def update_status():
                return "Running" if self.is_watching else "Stopped"
            
            async def start_watching():
                if not self.is_watching:
                    self.is_watching = True
                    self._watch_task = asyncio.create_task(self._watch_service())
                    return "Running"
                return "Already running"
            
            async def stop_watching():
                if self.is_watching and self._watch_task:
                    self.is_watching = False
                    self._watch_task.cancel()
                    return "Stopped"
                return "Already stopped"
            
            async def check_updates():
                try:
                    await self.sentinel.check_updates()
                    return "Updates check completed. Check the reports tab for details."
                except Exception as e:
                    return f"Error checking updates: {str(e)}"
            
            def remove_repository(repo_path: str):
                try:
                    if not repo_path or '/' not in repo_path:
                        return [
                            repo_list.value if repo_list.value else [],  # repo_list
                            gr.update(choices=repo_list.value),  # repo_select
                            gr.update(choices=repo_list.value),  # repo_input
                            "Error: Repository should be in format 'owner/repo'"  # status_message
                        ]
                    
                    owner, repo = repo_path.split('/')
                    self.sentinel.repo_remove(owner, repo)
                    return get_repository_list() + ["Repository removed successfully"]
                except Exception as e:
                    logger.error(f"Error removing repository: {e}")
                    return [
                        repo_list.value if repo_list.value else [],  # repo_list
                        gr.update(choices=repo_list.value),  # repo_select
                        gr.update(choices=repo_list.value),  # repo_input
                        f"Error removing repository: {str(e)}"  # status_message
                    ]
            
            def add_repository(repo_path: str, track_items: List[str]):
                try:
                    if not repo_path or '/' not in repo_path:
                        return [
                            repo_list.value if repo_list.value else [],  # repo_list
                            gr.update(choices=repo_list.value),  # repo_select
                            gr.update(choices=repo_list.value),  # repo_input
                            "Error: Repository should be in format 'owner/repo'"  # status_message
                        ]
                    
                    owner, repo = repo_path.split('/')
                    self.sentinel.repo_add(owner, repo, track_items)
                    return get_repository_list() + ["Repository added successfully"]
                except Exception as e:
                    logger.error(f"Error adding repository: {e}")
                    return [
                        repo_list.value if repo_list.value else [],  # repo_list
                        gr.update(choices=repo_list.value),  # repo_select
                        gr.update(choices=repo_list.value),  # repo_input
                        f"Error adding repository: {str(e)}"  # status_message
                    ]
            
            def get_repository_list():
                try:
                    repos = self.sentinel.subscription_manager.get_subscriptions()
                    if not repos:  # 如果没有仓库，返回空列表
                        return [
                            [],  # repo_list
                            gr.update(choices=[]),  # repo_select
                            gr.update(choices=[])  # repo_input
                        ]
                    
                    repo_data = [[repo['owner'], repo['repo'], ', '.join(repo['track'])] for repo in repos]
                    choices = [f"{repo['owner']}/{repo['repo']}" for repo in repos]
                    return [
                        repo_data,  # repo_list
                        gr.update(choices=choices),  # repo_select
                        gr.update(choices=choices)  # repo_input
                    ]
                except Exception as e:
                    logger.error(f"Error getting repository list: {e}")
                    return [
                        [],  # repo_list
                        gr.update(choices=[]),  # repo_select
                        gr.update(choices=[])  # repo_input
                    ]
            
            async def generate_report(report_type: str, repository: str):
                try:
                    if not repository:
                        return "Please select a repository"
                    
                    if '/' not in repository:
                        return "Invalid repository format. Should be 'owner/repo'"
                    
                    owner, repo = repository.split('/')
                    progress_data = await self.sentinel.github_client.get_daily_progress(owner, repo)
                    
                    if report_type == "Progress Report":
                        return self.sentinel.report_generator.generate_daily_progress_report(progress_data)
                    elif report_type == "AI Summary":
                        # Generate progress report first
                        progress_report = self.sentinel.report_generator.generate_daily_progress_report(progress_data)
                        
                        # Save it temporarily
                        today = datetime.now().strftime("%Y-%m-%d")
                        reports_dir = os.path.join("reports", "daily")
                        os.makedirs(reports_dir, exist_ok=True)
                        progress_file = os.path.join(reports_dir, f"progress_{today}.md")
                        
                        with open(progress_file, 'w', encoding='utf-8') as f:
                            f.write(progress_report)
                        
                        # Generate AI summary
                        summary = await self.sentinel.ai_report_generator.generate_daily_summary(progress_file)
                        return summary
                    else:
                        logger.error(f"Unknown report type: {report_type}")
                        return f"Unknown report type: {report_type}"
                except Exception as e:
                    logger.error(f"Error generating report: {e}")
                    return f"Error generating report: {str(e)}"
            
            def load_config():
                return self.sentinel.config
            
            def save_config(config_yaml: str):
                try:
                    # Save configuration
                    config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
                    with open(config_path, 'w') as f:
                        f.write(config_yaml)
                    return "Configuration saved successfully"
                except Exception as e:
                    return f"Error saving configuration: {str(e)}"
            
            # Wire up event handlers
            watch_button.click(fn=start_watching, outputs=status_text)
            stop_button.click(fn=stop_watching, outputs=status_text)
            check_button.click(fn=check_updates, outputs=report_output)
            
            add_repo_button.click(
                fn=add_repository,
                inputs=[repo_input, track_input],
                outputs=[repo_list, repo_select, repo_input, status_message]
            )
            remove_repo_button.click(
                fn=remove_repository,
                inputs=[repo_input],
                outputs=[repo_list, repo_select, repo_input, status_message]
            )
            refresh_repos_button.click(
                fn=get_repository_list,
                outputs=[repo_list, repo_select, repo_input]
            )
            
            generate_report_button.click(
                fn=generate_report,
                inputs=[report_type, repo_select],
                outputs=report_view
            )
            
            save_config_button.click(
                fn=save_config,
                inputs=[config_text],
                outputs=config_status
            )
            reload_config_button.click(fn=load_config, outputs=config_text)
            
            # Initial setup
            config_text.value = load_config()
            
        return interface
    
    async def _watch_service(self):
        """Background watch service implementation"""
        try:
            self.sentinel.schedule_jobs()
            while self.is_watching:
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Watch service error: {e}")
            self.is_watching = False

def launch_web_interface(config_path: str = "config/config.yaml"):
    """Launch the web interface"""
    sentinel = GitHubSentinel(config_path)
    web_ui = WebInterface(sentinel)
    interface = web_ui.create_interface()
    interface.queue()  # Enable queuing for async operations
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,  # Default Gradio port
        share=False,  # Disable public link
        show_error=True  # Show detailed error messages
    ) 