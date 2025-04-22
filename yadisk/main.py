from telegrambot import TelegramBot
from config import load_config

def main():
    config = load_config()
    bot = TelegramBot(config)
    bot.run()

if __name__ == "__main__":
    main()