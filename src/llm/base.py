from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class LLMBase(ABC):
    """LLM 基类，定义通用接口"""
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        聊天补全接口
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
            temperature: 温度参数，控制随机性，范围 0-2，默认 0.7
            max_tokens: 最大生成 token 数，默认 None（由模型决定）
            stream: 是否流式输出，默认 False
            
        Returns:
            Dict[str, Any]: 模型响应
        """
        pass
        
    @abstractmethod
    async def embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        文本嵌入接口
        
        Args:
            texts: 待嵌入的文本列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
        
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        获取文本的 token 数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: token 数量
        """
        pass 