from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound

from logic.services import filtering_category, view_in_cart, add_to_cart, remove_from_cart
from .models import DATABASE


def products_view(request):
    if request.method == "GET":
        id_ = request.GET.get('id')
        if id_:
            if id_ in DATABASE:
                return JsonResponse(DATABASE.get(id_), json_dumps_params={'ensure_ascii': False,
                                                         'indent': 4})
            else:
                return HttpResponseNotFound("Данного продукта нет в базе данных")


        category_key = request.GET.get("category")  # Считали 'category'
        if ordering_key := request.GET.get("ordering"):  # Если в параметрах есть 'ordering'
            if request.GET.get("reverse") and request.GET.get("reverse").lower() == 'true':# Если в параметрах есть 'ordering' и 'reverse'=True
                data = filtering_category(DATABASE,
                                          category_key=category_key,
                                          ordering_key=ordering_key,
                                          reverse=True)  # TODO Использовать filtering_category и провести фильтрацию с параметрами category, ordering, reverse=True
            else:  # Если не обнаружили в адресно строке ...&reverse=true , значит reverse=False
                data = filtering_category(DATABASE,
                                          category_key=category_key,
                                          ordering_key=ordering_key,
                                          reverse=False)  # TODO Использовать filtering_category и провести фильтрацию с параметрами category, ordering, reverse=False
        else:
            data = filtering_category(DATABASE,
                                     category_key=category_key)  # TODO Использовать filtering_category и провести фильтрацию с параметрами category
        # В этот раз добавляем параметр safe=False, для корректного отображения списка в JSON
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False,
                                                                 'indent': 4})



def shop_view(request):
    if request.method == "GET":
        with open('store/shop.html', encoding="utf-8") as f:
            data = f.read()  # Читаем HTML файл
        return HttpResponse(data)  # Отправляем HTML файл как ответ


def products_page_view(request, page):
    if request.method == "GET":
        if isinstance(page, str):
            for data in DATABASE.values():
                if data['html'] == page:  # Если значение переданного параметра совпадает именем html файла
                    with open(f'store/products/{page}.html', encoding="utf-8") as f:
                        res = f.read()
                    return HttpResponse(res)
        elif isinstance(page, int):
            data = DATABASE.get(str(page))  # Получаем какой странице соответствует данный id
            if data:
                with open(f'store/products/{data["html"]}.html', encoding="utf-8") as f:
                    res = f.read()
                return HttpResponse(res)
        return HttpResponse(status=404)




def cart_view(request):
    if request.method == "GET":
        data = view_in_cart() # TODO Вызвать ответственную за это действие функцию
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                     'indent': 4})


def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(id_product) # TODO Вызвать ответственную за это действие функцию и передать необходимые параметры
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(id_product) # TODO Вызвать ответственную за это действие функцию и передать необходимые параметры
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})
