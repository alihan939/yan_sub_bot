from yadisk.telegrambot import TelegramBot
from yadisk.config import load_config

if __name__ == "__main__":
    config = load_config()
    bot = TelegramBot(config)
    bot.run()
