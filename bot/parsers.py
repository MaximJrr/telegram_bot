import requests
from bs4 import BeautifulSoup


def parse_category_dishes():
    request = requests.get('https://povar.ru/')
    soup = BeautifulSoup(request.text, 'html.parser')
    category_dishes = {}
    categories = soup.find_all(class_='fmHead')

    for category in categories:
        category_name = category.text
        category_dishes[category_name] = []

        dishes = category.find_next('div').find_all(class_='fmItem')

        for dish in dishes:
            dish_name = dish.text
            category_dishes[category_name].append(dish_name)

    return category_dishes
