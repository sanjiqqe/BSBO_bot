
import httpx


# Получение случайной фотографии котика
async def get_cat_photo():
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://api.thecatapi.com/v1/images/search"
        )
        response.raise_for_status()
        data = response.json()

    if not data or "url" not in data[0]:
        raise ValueError("В ответе API нет ссылки на фотографию")

    return data[0]["url"]


# Получение ссылки на аватар робота
def get_robot_avatar_url(user_id):
    return f"https://robohash.org/{user_id}?set=set1"


# Получение примерного возраста по имени
async def get_age_by_name(name):
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://api.agify.io",
            params={"name": name}
        )
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, dict):
        raise ValueError("Некорректный ответ API")

    return data


# Описание погодных условий
def get_weather_description(code):
    descriptions = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Изморозь",
        51: "Лёгкая морось",
        53: "Умеренная морось",
        55: "Сильная морось",
        61: "Небольшой дождь",
        63: "Умеренный дождь",
        65: "Сильный дождь",
        71: "Небольшой снег",
        73: "Умеренный снег",
        75: "Сильный снег",
        80: "Ливень",
        81: "Умеренный ливень",
        82: "Сильный ливень",
        95: "Гроза",
        96: "Гроза с небольшим градом",
        99: "Гроза с сильным градом"
    }

    return descriptions.get(code, "Неизвестные погодные условия")


# Получение текущей погоды по координатам
async def get_weather(latitude, longitude):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            }
        )

        response.raise_for_status()
        data = response.json()

    if "current" not in data:
        raise ValueError("В ответе API нет текущей погоды")

    return data["current"]
