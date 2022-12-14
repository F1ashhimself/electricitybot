from pydantic import BaseSettings


class Settings(BaseSettings):
    api_token: str
    chat_id: str
    ip_to_check: str
    retries_count: int = 3
    timeout: int = 60
    thread_id: int = None

    class Config:
        env_file = ".env"


settings = Settings()
