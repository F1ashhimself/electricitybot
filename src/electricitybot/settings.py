from contextlib import contextmanager
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


@contextmanager
def override_settings(**settings_to_override):
    """
    Decorator to override settings for tests.
    """
    old_settings = {}
    for setting_key, setting_value in settings_to_override.items():
        old_settings[setting_key] = getattr(settings, setting_key)
        setattr(settings, setting_key, setting_value)

    yield

    for setting_key, setting_value in old_settings.items():
        setattr(settings, setting_key, setting_value)
