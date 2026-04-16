"""项目配置中心。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置。"""

    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL_NAME: str = "myqwen:latest"

    # Docker 沙箱配置
    SANDBOX_DOCKER_IMAGE: str = "gcc:13"
    SANDBOX_MEMORY_LIMIT: str = "256m"
    SANDBOX_CPU_QUOTA: int = 50000
    SANDBOX_TIMEOUT_SECONDS: int = 5

    # Submission 内存缓存策略
    SUBMISSION_TTL_MINUTES: int = 15
    MAX_SUBMISSIONS_IN_MEMORY: int = 300

    # 安全策略：限流与输入约束
    ALLOWED_LANGUAGES: str = "cpp"
    MAX_SOURCE_CODE_LENGTH: int = 20000
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 20

    # 日志级别（DEBUG/INFO/WARNING/ERROR）
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
