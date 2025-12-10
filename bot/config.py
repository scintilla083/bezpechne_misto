import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Настройки бота"""
    bot_token: str = os.getenv("BOT_TOKEN", "")

    def __post_init__(self):
        if not self.bot_token:
            raise ValueError(
                "BOT_TOKEN не установлен! Пожалуйста, создайте .env файл "
                "и добавьте туда BOT_TOKEN=your_token_here"
            )


settings = Settings()