"""大模型客户端

封装 OpenAI 兼容 API 调用，支持系统提示词和对话历史。
"""

from typing import Optional
from openai import OpenAI
import httpx

from config import settings


class LLMClient:
    """OpenAI 兼容 LLM 客户端"""

    def __init__(self):
        # 绕过系统 HTTP 代理，避免 SSL 中断
        http_client = httpx.Client(trust_env=False, timeout=120.0)
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_API_BASE,
            http_client=http_client,
        )
        self.model = settings.LLM_MODEL

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """发送对话请求

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 对话历史 [{"role": "user"/"assistant", "content": "..."}]
            temperature: 生成温度
            max_tokens: 最大输出 token

        Returns:
            模型回复文本
        """
        messages: list[dict] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def chat_json(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """发送对话请求，强制返回 JSON 格式（作为字符串）"""
        full_message = message + "\n\n请以 JSON 格式回答，不要包含其他内容。"
        return self.chat(full_message, system_prompt, history, temperature, max_tokens)

    def is_configured(self) -> bool:
        """检查 API Key 是否已配置"""
        return bool(settings.LLM_API_KEY and settings.LLM_API_KEY != "your-api-key-here")


# 全局单例
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
