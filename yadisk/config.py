from pydantic import BaseModel
import tomli

class MarzbanConfig(BaseModel):
    host: str
    username: str
    password: str

class TelegramConfig(BaseModel):
    bot_token: str
    admin_id: int

class YandexConfig(BaseModel):
    oauth_token: str

class Config(BaseModel):
    marzban: MarzbanConfig
    telegram: TelegramConfig
    yandex: YandexConfig

def load_config() -> Config:
    with open("config.toml", "rb") as f:
        data = tomli.load(f)
    return Config(**data)
