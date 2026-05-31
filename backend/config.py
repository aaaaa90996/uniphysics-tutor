"""UniPhysics Tutor 后端配置"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM 配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")

    # Embedding 模型
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # TTS
    TTS_ENABLED: bool = os.getenv("TTS_ENABLED", "true").lower() == "true"
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "edge-tts")

    # 路径
    KNOWLEDGE_BASE_PATH: str = os.getenv(
        "KNOWLEDGE_BASE_PATH",
        os.path.join(os.path.dirname(__file__), "..", "knowledge_base"),
    )
    PROMPTS_PATH: str = os.getenv(
        "PROMPTS_PATH",
        os.path.join(os.path.dirname(__file__), "..", "prompts"),
    )

    # Chroma 持久化目录
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        os.path.join(os.path.dirname(__file__), "chroma_db"),
    )

    # 服务端口
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # 校验器开关
    VALIDATOR_ENABLED: bool = os.getenv("VALIDATOR_ENABLED", "true").lower() == "true"
    VALIDATOR_MAX_RETRIES: int = int(os.getenv("VALIDATOR_MAX_RETRIES", "2"))


settings = Settings()
