import logging
from typing import Dict, Any, List, Optional
import tiktoken
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion

from .base import LLMBase

logger = logging.getLogger(__name__)

class OpenAILLM(LLMBase):
    """OpenAI LLM 实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 OpenAI LLM
        
        Args:
            config: 配置信息，包含 API key 等
        """
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config['api_key'],
            organization=config.get('organization'),
            base_url=config.get('base_url', 'https://api.openai.com/v1')
        )
        self.model = config.get('model', 'gpt-4')
        self.encoding = tiktoken.encoding_for_model(self.model)
        
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
            messages: 对话历史
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            stream: 是否流式输出
            
        Returns:
            Dict[str, Any]: 模型响应
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                assert isinstance(response, AsyncStream)
                chunks = []
                async for chunk in response:
                    chunks.append(chunk.choices[0].delta.content or "")
                return {
                    'content': "".join(chunks),
                    'role': 'assistant'
                }
            else:
                assert isinstance(response, ChatCompletion)
                return {
                    'content': response.choices[0].message.content,
                    'role': response.choices[0].message.role
                }
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
            
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
        try:
            # 使用 text-embedding-3-small 模型
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Error in embeddings: {e}")
            raise
            
    def get_token_count(self, text: str) -> int:
        """
        获取文本的 token 数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: token 数量
        """
        return len(self.encoding.encode(text)) 