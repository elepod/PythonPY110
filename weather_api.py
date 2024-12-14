import json

import requests
from datetime import datetime

# Словарь перевода значений направления ветра
DIRECTION_TRANSFORM = {
    'n': 'северное',
    'nne': 'северо - северо - восточное',
    'ne': 'северо - восточное',
    'ene': 'восточно - северо - восточное',
    'e': 'восточное',
    'ese': 'восточно - юго - восточное',
    'se': 'юго - восточное',
    'sse': 'юго - юго - восточное',
    's': 'южное',
    'ssw': 'юго - юго - западное',
    'sw': 'юго - западное',
    'wsw': 'западно - юго - западное',
    'w': 'западное',
    'wnw': 'западно - северо - западное',
    'nw': 'северо - западное',
    'nnw': 'северо - северо - западное',
    'c': 'штиль',
}


def current_weather(lat: float, lon: float) -> dict:
    """
    Function that return the weather for latitude and longitude
    :param lat: latitude
    :param lon: longitude
    :return: data as a dict
    """
    token = 'a58f910e-ef9e-43f1-aa15-0f9bc1bde3f1'  # Вставить ваш токен
    url = f"https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}"  # Если вдруг используете тариф «Погода на вашем сайте»
    # то вместо forecast используйте informers. url = f"https://api.weather.yandex.ru/v2/informers?lat={lat}&lon={lon}"
    headers = {"X-Yandex-API-Key": f"{token}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    # Данная реализация приведена для тарифа «Тестовый», если у вас Тариф «Погода на вашем сайте», то закомментируйте пару строк указанных ниже
    result = {
        #'city': data['geo_object']['locality']['name'],  # Если используете Тариф «Погода на вашем сайте», то закомментируйте эту строку
        'time': datetime.fromtimestamp(data['fact']['uptime']).strftime("%H:%M"),  # Если используете Тариф «Погода на вашем сайте», то закомментируйте эту строку
        'temp': data['fact']['temp'],  # TODO Реализовать вычисление температуры из данных полученных от API
        'feels_like_temp': data['fact']['feels_like'],  # TODO Реализовать вычисление ощущаемой температуры из данных полученных от API
        'pressure': data['fact']['pressure_mm'],  # TODO Реализовать вычисление давления из данных полученных от API
        'humidity': data['fact']['humidity'],  # TODO Реализовать вычисление влажности из данных полученных от API
        'wind_speed': data['fact']['wind_speed'],  # TODO Реализовать вычисление скорости ветра из данных полученных от API
        'wind_gust': data['fact']['wind_gust'],  # TODO Реализовать вычисление скорости порывов ветка из данных полученных от API
        'wind_dir': DIRECTION_TRANSFORM.get(data['fact']['wind_dir']),  # Если используете Тариф «Погода на вашем сайте», то закомментируйте эту строку
    }
    return result

def current_weather_api_weather(city):
    token = 'd45ec687f6674449bbf153647243011'
    params = {'key': token, 'q': city}
    url = f'https://api.weatherapi.com/v1/current.json'
    response = requests.get(url, params=params)
    data = response.json()
    result = {
        'city': data["location"]["name"],
        'country': data["location"]["country"],
        'time': data['current']['last_updated'],
        'temp': data["current"]["temp_c"],
        'feels_like_temp': data["current"]["feelslike_c"],
    }
    return result


if __name__ == "__main__":
    # print(current_weather(59.93, 30.31))  # Проверка работы для координат Санкт-Петербурга
    print(current_weather_api_weather('London'))
