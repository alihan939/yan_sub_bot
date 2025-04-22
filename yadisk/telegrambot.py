from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from marzban import MarzbanClient
from yandex_disk import YandexDiskClient
from config import Config

class TelegramBot:
    def __init__(self, config: Config):
        self.config = config
        self.marzban = MarzbanClient(config.marzban)
        self.yandex = YandexDiskClient(config.yandex.oauth_token)
        
        self.app = Application.builder().token(config.telegram.bot_token).build()
        
        # Регистрация обработчиков
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.search_handler))

    async def start(self, update: Update, _):
        if update.effective_user.id != self.config.telegram.admin_id:
            await update.message.reply_text("Доступ запрещен!")
            return
            
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить данные", callback_data="update")],
            [InlineKeyboardButton("🔍 Поиск подписки", callback_data="search")]
        ]
        await update.message.reply_text(
            "Панель управления Marzban:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def button_handler(self, update: Update, _):
        query = update.callback_query
        if query.data == "update":
            await self.marzban.sync_data()
            await query.answer("Данные успешно обновлены!")
        elif query.data == "search":
            await query.message.reply_text("Введите название подписки:")

    async def search_handler(self, update: Update, _):
        username = update.message.text
        user = await self.marzban.get_user(username)
        
        if not user:
            await update.message.reply_text("Подписка не найдена!")
            return
            
        # Загрузка файла на Яндекс.Диск и получение ссылки
        file_path = f"/marzban_subscriptions/{username}.txt"
        content = f"Подписка: {username}\nСсылка: {user.subscription_url}"
        public_url = await self.yandex.upload_and_publish(file_path, content)
        
        await update.message.reply_text(f"🔗 Ссылка на подписку:\n{public_url}")

    def run(self):
        self.app.run_polling()