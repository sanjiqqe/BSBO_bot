
import logging
import httpx

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from utils import (
    get_cat_photo,
    get_robot_avatar_url,
    get_age_by_name,
    get_weather,
    get_weather_description
)


logger = logging.getLogger(__name__)


# Создаём клавиатуру
keyboard = [
    ["Мой ID", "Помощь"],
    ["Фото котика", "Аватар робота"],
    ["Возраст по имени"],
    [KeyboardButton("Отправить геолокацию", request_location=True)]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_for_name"] = False

    logger.info("Пользователь запустил команду /start")

    await update.message.reply_text(
        "Привет! Я бот MIREA.\n"
        "Выбери действие с помощью кнопок ниже.",
        reply_markup=reply_markup
    )


# Обработка нажатий на кнопки и ввода имени
async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text.strip()

    buttons = [
        "Мой ID",
        "Помощь",
        "Фото котика",
        "Аватар робота",
        "Возраст по имени"
    ]

    # Если бот ожидает имя пользователя
    if context.user_data.get("waiting_for_name"):
        if text not in buttons:
            context.user_data["waiting_for_name"] = False

            if not any(char.isalpha() for char in text):
                logger.warning("Получен некорректный ввод имени")

                await update.message.reply_text(
                    "Пожалуйста, введи корректное имя."
                )
                return

            logger.info("Пользователь запросил определение возраста по имени")

            await update.message.reply_text(
                "Определяю примерный возраст..."
            )

            try:
                data = await get_age_by_name(text)

                age = data.get("age")
                count = data.get("count")

                if age is None:
                    logger.warning("API не вернул возраст для указанного имени")

                    await update.message.reply_text(
                        "Не удалось определить возраст по этому имени."
                    )
                else:
                    logger.info("Возраст по имени успешно получен")

                    await update.message.reply_text(
                        f"Имя: {data.get('name', text)}\n"
                        f"Предполагаемый возраст: {age} лет\n"
                        f"Количество учтённых записей: {count}"
                    )

            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                logger.exception("Ошибка при получении возраста по имени")

                await update.message.reply_text(
                    "Не удалось получить данные. Попробуй ещё раз."
                )

            return

        context.user_data["waiting_for_name"] = False

    if text == "Мой ID":
        logger.info("Пользователь запросил свой Telegram ID")

        await update.message.reply_text(
            f"Твой Telegram ID: {update.effective_user.id}"
        )

    elif text == "Помощь":
        logger.info("Пользователь открыл раздел помощи")

        await update.message.reply_text(
            "Я учебный бот MIREA.\n"
            "Выбери одну из кнопок меню."
        )

    elif text == "Фото котика":
        logger.info("Пользователь запросил фотографию котика")

        await update.message.reply_text("Ищу для тебя котика...")

        try:
            photo_url = await get_cat_photo()

            await update.message.reply_photo(
                photo=photo_url,
                caption="Вот твой котик!"
            )

            logger.info("Фотография котика успешно отправлена")

        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, TelegramError):
            logger.exception("Ошибка при получении или отправке фотографии котика")

            await update.message.reply_text(
                "Не удалось получить фотографию. Попробуй ещё раз."
            )

    elif text == "Аватар робота":
        logger.info("Пользователь запросил аватар робота")

        await update.message.reply_text(
            "Создаю для тебя аватар..."
        )

        try:
            avatar_url = get_robot_avatar_url(
                update.effective_user.id
            )

            await update.message.reply_photo(
                photo=avatar_url,
                caption="Твой робот-аватар!"
            )

            logger.info("Аватар робота успешно отправлен")

        except (TelegramError, httpx.HTTPError):
            logger.exception("Ошибка при создании или отправке аватара")

            await update.message.reply_text(
                "Не удалось создать аватар. Попробуй ещё раз."
            )

    elif text == "Возраст по имени":
        logger.info("Пользователь выбрал функцию определения возраста")

        context.user_data["waiting_for_name"] = True

        await update.message.reply_text(
            "Введи имя, чтобы узнать предполагаемый возраст."
        )


# Обработка отправленной геолокации
async def location_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    location = update.message.location

    if location is None:
        logger.warning("Получено сообщение без данных геолокации")

        await update.message.reply_text(
            "Не удалось получить геолокацию. Попробуй ещё раз."
        )
        return

    latitude = location.latitude
    longitude = location.longitude

    logger.info("Пользователь отправил геолокацию для получения погоды")

    await update.message.reply_text(
        "Получаю погоду по твоей геолокации..."
    )

    try:
        current = await get_weather(latitude, longitude)

        temperature = current["temperature_2m"]
        feels_like = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        precipitation = current["precipitation"]
        weather_code = current["weather_code"]

        description = get_weather_description(weather_code)

        message = (
            "Погода по твоей геолокации:\n\n"
            f"Состояние: {description}\n"
            f"Температура: {temperature} °C\n"
            f"Ощущается как: {feels_like} °C\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind} км/ч\n"
            f"Осадки: {precipitation} мм"
        )

        await update.message.reply_text(message)

        logger.info("Данные о погоде успешно получены и отправлены")

    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        logger.exception("Ошибка при получении данных о погоде")

        await update.message.reply_text(
            "Не удалось получить данные о погоде. "
            "Попробуй отправить геолокацию ещё раз."
        )
