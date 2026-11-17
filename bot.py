
import os

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

from handlers import start, button_handler, location_handler


# Создание и запуск Telegram-бота
def run_bot():
    load_dotenv()

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError(
            "Не найден токен BOT_TOKEN в файле .env"
        )

    app = ApplicationBuilder().token(token).build()

    # Подключаем обработчик команды /start
    app.add_handler(CommandHandler("start", start))

    # Подключаем обработчик геолокации
    app.add_handler(
        MessageHandler(
            filters.LOCATION,
            location_handler
        )
    )

    # Подключаем обработчик текстовых сообщений и кнопок
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler
        )
    )

    print("Бот запущен! Для остановки нажми Ctrl+C.")

    app.run_polling()
