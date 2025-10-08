from pydantic_settings import BaseSettings
from pydantic import BaseModel


class LLMConfig(BaseModel):
    model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    device: str | None = None
    max_new_tokens: int = 500
    temperature: float = 0.3
    top_k: int = 50
    top_p: float = 0.9


class AppConfig(BaseModel):
    docs_url: str = "/docs"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class Config(BaseSettings):
    llm_config: LLMConfig = LLMConfig()
    app_config: AppConfig = AppConfig()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


config = Config()
