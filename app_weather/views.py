from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from weather_api import current_weather_api_weather


def my_view(request):
    if request.method == "GET":
        # data = current_weather(59.93, 30.31)  # Результат работы функции current_weather
        # А возвращаем объект JSON. Параметр json_dumps_params используется, чтобы передать ensure_ascii=False
        # как помните это необходимо для корректного отображения кириллицы
        data = current_weather_api_weather('London')
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                     'indent': 4})

def weather_view(request):
    if request.method == "GET":
        city = request.GET.get('q')  # данные придут в виде строки
        print(city)
        if city:
            data = current_weather_api_weather(city=city)
        else:
            data = current_weather_api_weather(city='London')
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                     'indent': 4})