Telegram Marzban Bot

Бот на Python для автоматического создания и отправки VPN-конфигов с помощью Marzban и Яндекс.Диска.

Возможности

Управление через Telegram

Генерация и публикация VPN-конфигов (VLESS/VMess)

Хранение конфигов на Яндекс.Диске

Поддержка Docker


Установка

1. Клонируйте репозиторий и перейдите в папку:

git clone https://github.com/you/project.git
cd project

2. Настройте переменные окружения

Создайте .env на основе шаблона:

cp .env.example .env

Открой .env и впиши свои значения:

TELEGRAM_BOT_TOKEN=...         # токен Telegram-бота
TELEGRAM_ADMIN_ID=...          # Telegram ID администратора

MARZBAN_BASE_URL=https://...   # URL Marzban
MARZBAN_API_KEY=...            # API-ключ от Marzban

YANDEX_OAUTH_TOKEN=...         # OAuth-токен от Яндекс.Диска

3. Сборка и запуск через Docker

docker build -t telegram-marzban-bot .
docker run -d --name bot --env-file .env --restart=always telegram-marzban-bot

Структура проекта

project/
├── Dockerfile
├── main.py
├── requirements.txt
├── .env.example
└── yadisk/
    ├── telegrambot.py
    ├── yandex_disk.py
    ├── config.py
    └── models.py

Лицензия

MIT