import os
import logging
from typing import Dict, Any, List
from datetime import datetime
import yaml

from llm import LLMFactory

logger = logging.getLogger(__name__)

class AIReportGenerator:
    """AI 驱动的报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 AI 报告生成器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.llm = LLMFactory.create(
            config['llm']['type'],
            config['llm'][config['llm']['type']]
        )
        
    async def generate_daily_summary(self, progress_file: str) -> str:
        """
        生成每日项目总结报告
        
        Args:
            progress_file: 进展报告文件路径
            
        Returns:
            str: 生成的报告内容
        """
        try:
            # 读取进展报告
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_content = f.read()
                
            # 构建 prompt
            messages = [
                {
                    "role": "system",
                    "content": """你是一个专业的技术项目经理，负责生成项目的每日报告。请你用正式的语气，将提供的GitHub项目进展整理成一份简洁但信息完整的每日报告。

报告应该包含以下部分：
1. 报告标题和基本信息（日期、项目名称等）
2. 项目概览（简要统计信息）
3. 主要更新内容（重要的PR和Issue）
4. 问题和风险（如果有的话）
5. 下一步工作建议

请注意：
- 使用中文
- 使用专业的项目管理语言
- 重点突出重要的更新和变化
- 对问题进行分类和优先级排序
- 给出具有建设性的建议"""
                },
                {
                    "role": "user",
                    "content": f"请根据以下GitHub项目进展内容，生成一份正式的每日项目报告（使用Markdown格式）：\n\n{progress_content}"
                }
            ]
            
            # 调用 GPT-4 生成报告
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.7
            )
            
            return response['content']
            
        except Exception as e:
            logger.error(f"Error generating AI report: {e}")
            raise
            
    async def process_daily_reports(self, reports_dir: str = "reports") -> None:
        """
        处理所有每日进展报告
        
        Args:
            reports_dir: 报告目录
        """
        try:
            # 获取今天的日期
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 使用正确的daily目录
            daily_dir = os.path.join(reports_dir, "daily")
            if not os.path.exists(daily_dir):
                logger.error(f"Reports directory not found: {daily_dir}")
                raise FileNotFoundError(f"Reports directory not found: {daily_dir}")
            
            # 查找所有今天的进展报告
            found_reports = False
            for filename in os.listdir(daily_dir):
                if filename.endswith(f"progress_{today}.md"):
                    found_reports = True
                    logger.info(f"Processing report: {filename}")
                    
                    # 生成 AI 总结报告
                    progress_file = os.path.join(daily_dir, filename)
                    summary_content = await self.generate_daily_summary(progress_file)
                    
                    # 保存总结报告
                    summary_filename = filename.replace("progress", "summary")
                    summary_file = os.path.join(daily_dir, summary_filename)
                    
                    with open(summary_file, 'w', encoding='utf-8') as f:
                        f.write(summary_content)
                        
                    logger.info(f"Generated summary report: {summary_filename}")
            
            if not found_reports:
                logger.error(f"No progress reports found for today ({today})")
                raise FileNotFoundError(f"No progress reports found for today ({today})")
                    
        except Exception as e:
            logger.error(f"Error processing daily reports: {e}")
            raise 