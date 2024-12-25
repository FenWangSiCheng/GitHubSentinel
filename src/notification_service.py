import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from slack_sdk.web.async_client import AsyncWebClient

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知服务
        
        Args:
            config: 通知配置信息
        """
        self.config = config
        self.email_config = config.get('email', {})
        self.slack_config = config.get('slack', {})
        
    async def send_notifications(self, content: str) -> None:
        """
        发送通知
        
        Args:
            content: 通知内容
        """
        tasks = []
        
        if self.email_config.get('enabled', False):
            tasks.append(self._send_email(content))
            
        if self.slack_config.get('enabled', False):
            tasks.append(self._send_slack(content))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def send_error_notification(self, error_message: str) -> None:
        """
        发送错误通知
        
        Args:
            error_message: 错误信息
        """
        error_report = f"""
# Error Report
An error occurred during the update check:

```
{error_message}
```
"""
        await self.send_notifications(error_report)
        
    async def _send_email(self, content: str) -> None:
        """
        发送邮件通知
        
        Args:
            content: 通知内容
        """
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'GitHub Repository Updates'
            msg['From'] = self.email_config['username']
            msg['To'] = ', '.join(self.email_config['recipients'])
            
            # 添加纯文本和HTML版本
            text_part = MIMEText(content, 'plain')
            html_part = MIMEText(self._convert_markdown_to_html(content), 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.email_config['username'],
                    self.email_config['password']
                )
                server.send_message(msg)
                
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            raise
            
    async def _send_slack(self, content: str) -> None:
        """
        发送Slack通知
        
        Args:
            content: 通知内容
        """
        try:
            webhook_url = self.slack_config['webhook_url']
            channel = self.slack_config['channel']
            
            # 将报告分块，确保不超过Slack消息长度限制
            chunks = self._chunk_message(content, max_length=3000)
            
            async with aiohttp.ClientSession() as session:
                for i, chunk in enumerate(chunks, 1):
                    payload = {
                        'channel': channel,
                        'text': f"GitHub Updates Report (Part {i}/{len(chunks)}):\n{chunk}"
                    }
                    
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status != 200:
                            raise Exception(
                                f"Slack API returned status {response.status}"
                            )
                            
            logger.info("Slack notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            raise
            
    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """
        将Markdown转换为HTML
        
        Args:
            markdown_text: Markdown文本
            
        Returns:
            str: HTML文本
        """
        import markdown
        
        # 使用Python-Markdown转换
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite']
        )
        
        # 添加基本的样式
        return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 
                                   "Segoe UI", Helvetica, Arial, sans-serif;
                        line-height: 1.6;
                        padding: 20px;
                        max-width: 800px;
                        margin: 0 auto;
                    }}
                    pre {{
                        background-color: #f6f8fa;
                        padding: 16px;
                        border-radius: 6px;
                        overflow-x: auto;
                    }}
                    code {{
                        font-family: SFMono-Regular, Consolas, 
                                   "Liberation Mono", Menlo, monospace;
                    }}
                    h1, h2, h3 {{
                        border-bottom: 1px solid #eaecef;
                        padding-bottom: 0.3em;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
        </html>
        """
        
    def _chunk_message(self, message: str, max_length: int) -> List[str]:
        """
        将消息分块，确保每块不超过指定长度
        
        Args:
            message: 原始消息
            max_length: 每块的最大长度
            
        Returns:
            List[str]: 消息块列表
        """
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in message.split('\n'):
            line_length = len(line) + 1  # +1 for newline
            
            if current_length + line_length > max_length:
                # 当前块已满，保存并开始新块
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                # 添加行到当前块
                current_chunk.append(line)
                current_length += line_length
                
        # 添加最后一块
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks 