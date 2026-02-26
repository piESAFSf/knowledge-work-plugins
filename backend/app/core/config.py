from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Enterprise SaaS'
    debug: bool = False
    secret_key: str = 'change-me'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    database_url: str = 'postgresql+psycopg2://postgres:postgres@db:5432/saas'
    redis_url: str = 'redis://redis:6379/0'

    allowed_origins: str = 'http://localhost:5173'
    stripe_secret_key: str = ''
    stripe_webhook_secret: str = ''
    line_channel_secret: str = ''
    line_channel_access_token: str = ''
    openai_api_key: str = ''


settings = Settings()
