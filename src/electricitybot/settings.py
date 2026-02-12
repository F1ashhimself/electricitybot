from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    api_token: str
    chat_id: str
    ip_to_check: str
    retries_count: int = 3
    timeout: int = 60
    send_weekly_stats: bool = True
    stats_day_of_week: int = 1
    stats_hour: int = 12
    thread_id: Union[int, None] = None


settings = Settings()
