
import logging

from bot import run_bot


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Запуск программы
if __name__ == "__main__":
    logger.info("Запуск Telegram-бота")

    try:
        run_bot()

    except KeyboardInterrupt:
        logger.info("Работа бота остановлена пользователем")

    except Exception:
        logger.exception("Произошла критическая ошибка")
        raise
