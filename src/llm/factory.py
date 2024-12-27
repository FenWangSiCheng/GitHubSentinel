from typing import Dict, Any

from .base import LLMBase
from .openai_llm import OpenAILLM

class LLMFactory:
    """LLM 工厂类，用于创建不同的 LLM 实例"""
    
    @staticmethod
    def create(llm_type: str, config: Dict[str, Any]) -> LLMBase:
        """
        创建 LLM 实例
        
        Args:
            llm_type: LLM 类型，如 'openai'
            config: 配置信息
            
        Returns:
            LLMBase: LLM 实例
            
        Raises:
            ValueError: 不支持的 LLM 类型
        """
        if llm_type == 'openai':
            return OpenAILLM(config)
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}") 