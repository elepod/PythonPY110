from itertools import product
from lib2to3.fixes.fix_input import context

from django.contrib.auth import get_user
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
                                                                 'indent': 4},
                            context={
                                'product': data,
                                'category': category_key
                            })



# def shop_view(request):
#     if request.method == "GET":
#         with open('store/shop.html', encoding="utf-8") as f:
#             data = f.read()  # Читаем HTML файл
#         return HttpResponse(data)  # Отправляем HTML файл как ответ

from django.shortcuts import render

# def shop_view(request):
#     if request.method == "GET":
#         return render(request, 'store/shop.html', context={"products": DATABASE.values()})

def shop_view(request):
    if request.method == "GET":
        # Обработка фильтрации из параметров запроса
        category_key = request.GET.get("category")
        if ordering_key := request.GET.get("ordering"):
            if request.GET.get("reverse") in ('true', 'True'):
                data = filtering_category(DATABASE, category_key, ordering_key,
                                          True)
            else:
                data = filtering_category(DATABASE, category_key, ordering_key)
        else:
            data = filtering_category(DATABASE, category_key)
        return render(request, 'store/shop.html',
                      context={"products": data})


def products_page_view(request, page):
    if request.method == "GET":
        if isinstance(page, str):
            for data in DATABASE.values():
                if data['html'] == page:
                    some_products = [el for el in filtering_category(DATABASE, category_key=data['category'])
                                     if el['name'] != data['name']]
                    return render(request, "store/product.html",
                                  context={"product": data, 'some_products': some_products[:5]})

        elif isinstance(page, int):
            # Обрабатываем условие того, что пытаемся получить страницу товара по его id
            data = DATABASE.get(str(page))  # Получаем какой странице соответствует данный id
            if data:
                some_products = list(filter(lambda x: x['name'] != data['name'],
                                            filtering_category(DATABASE, category_key=data['category'])))
                return render(request, "store/product.html",
                              context={"product": data, 'some_products': some_products[:5]})

        return HttpResponse(status=404)

@login_required(login_url='login:login_view')
def cart_view(request):
    if request.method == "GET":
        current_user = get_user(request).username
        data = view_in_cart(request)[current_user]
        print(f'Cart: {data}')
        if request.GET.get('format') == 'JSON':
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                         'indent': 4})
        products = []  # Список продуктов
        for product_id, quantity in data['products'].items():
            product = DATABASE[product_id]  # 1. Получите информацию о продукте из DATABASE по его product_id. product будет словарём
            product['quantity'] = quantity
            product['price_after'] = product['price_after']
            # 2. в словарь product под ключом "quantity" запишите текущее значение товара в корзине
            product["price_total"] = f"{quantity * product['price_after']:.2f}"  # добавление общей цены позиции с ограничением в 2 знака
            # 3. добавьте product в список products
            products.append(product)
        return render(request, "store/cart.html", context={"products": products})

@login_required(login_url='login:login_view')
def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product) # TODO Вызвать ответственную за это действие функцию и передать необходимые параметры
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(request, id_product) # TODO Вызвать ответственную за это действие функцию и передать необходимые параметры
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})

def coupon_check_view(request, coupon_code):
    # DATA_COUPON - база данных купонов: ключ - код купона (name_coupon); значение - словарь со значением скидки в процентах и
    # значением действителен ли купон или нет
    DATA_COUPON = {
        "coupon": {
            "value": 10,
            "is_valid": True},
        "coupon_old": {
            "value": 20,
            "is_valid": False},
    }
    if request.method == "GET":
        # TODO Проверьте, что купон есть в DATA_COUPON, если он есть, то верните JsonResponse в котором по ключу "discount"
        if coupon_code in DATA_COUPON:
            coupon = DATA_COUPON[coupon_code]
            return JsonResponse({"discount": coupon['value'], "is_valid": coupon["is_valid"]})
        return JsonResponse({"answer": "Неверный купон"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})

def delivery_estimate_view(request):
    # База данных по стоимости доставки. Ключ - Страна; Значение словарь с городами и ценами; Значение с ключом fix_price
    # применяется если нет города в данной стране
    DATA_PRICE = {
        "Россия": {
            "Москва": {"price": 80},
            "Санкт-Петербург": {"price": 80},
            "fix_price": 100,
        },
    }
    if request.method == "GET":
        data = request.GET
        country = data.get('country')
        city = data.get('city')
        # TODO Реализуйте логику расчёта стоимости доставки, которая выполняет следующее:
        # Если в базе DATA_PRICE есть и страна (country) и существует город(city), то вернуть JsonResponse
        # со словарём, {"price": значение стоимости доставки}
        # Если в базе DATA_PRICE есть страна, но нет города, то вернуть JsonResponse со словарём,
        # {"price": значение фиксированной стоимости доставки}
        # Если нет страны, то вернуть HttpResponseNotFound("Неверные данные")
        if country in DATA_PRICE:
            if city in DATA_PRICE[country]:
                return JsonResponse({"price": DATA_PRICE[country][city]["price"]})
            else:
                return JsonResponse({"price": DATA_PRICE[country]["fix_price"]})
        return JsonResponse({"answer": "Неверные данные"},
                            status=404,
                            json_dumps_params={'ensure_ascii': False})

@login_required(login_url='login:login_view')
def cart_buy_now_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product)
        if result:
            return redirect("store:cart_view")

        return HttpResponseNotFound("Неудачное добавление в корзину")

def cart_remove_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(request, id_product)
        if result:
            return redirect("store:cart_view")

        return HttpResponseNotFound("Неудачное удаление из корзины")

