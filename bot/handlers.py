import requests
from aiogram import Bot, Dispatcher, executor, types
from config import headers
from bs4 import BeautifulSoup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
from parsers import parse_category_dishes

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)


async def on_startup(_):
    print("Bot started")


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text=f"Здравствуйте, {message.from_user.first_name}! Напишите название блюда, которое хотели"
                              f" бы найти, или вызовите комманду /menu для открытия категорий")
    await message.delete()


@dp.message_handler(commands=['menu'])
async def menu_command(message: types.Message):
    category_keyboard = InlineKeyboardMarkup()

    for category in parse_category_dishes():
        category_keyboard.add(InlineKeyboardButton(text=category, callback_data=f'category:{category}'))
    await message.answer("Выберите категорию блюд:", reply_markup=category_keyboard)
    await message.delete()


@dp.message_handler(content_types=['text'])
async def parser_dishes(message: types.Message):
    for page in range(1, 3):
        url = f"https://povar.ru/xmlsearch?query={message.text}&page={page}"
        request = requests.get(url, headers=headers)
        soup = BeautifulSoup(request.text, "html.parser")
        links = soup.find_all('div', class_='recipe')
        dishes_found = False

        for link in links:
            recipe_id = link.find(
                'div', class_='h3').find('a', class_='listRecipieTitle').get('href').split("-")[-1].split(".")[0]

            inline_button = InlineKeyboardButton("Посмотреть подробнее", callback_data=f"recipe:{recipe_id}")
            inline_markup = InlineKeyboardMarkup().add(inline_button)

            name = link.find('div', class_='h3').find('a', class_='listRecipieTitle').text
            description = link.find('p', class_='txt').text
            image = link.find('span', class_='a thumb hashString').find('img').get('src')
            dishes_found = True

            await bot.send_photo(
                message.chat.id,
                image,
                f"*{name}*\n_{description}_",
                reply_markup=inline_markup,
                parse_mode='markdown'
            )

    if not dishes_found:
        await bot.send_message(
            message.chat.id, f"К сожалению, блюдо <b>{message.text}</b> не найдено 😢", parse_mode='html'
        )
        await message.delete()


@dp.callback_query_handler(lambda query: query.data.startswith("recipe:"))
async def get_recipe_details(callback_query: types.CallbackQuery):
    recipe_id = callback_query.data.split(":")[1]
    recipe_url = f"https://povar.ru/recipes/picca_v_domashnih_usloviyah_v_duhovke-{recipe_id}.html"

    recipe_request = requests.get(recipe_url, headers=headers)
    recipe_soup = BeautifulSoup(recipe_request.text, "html.parser")
    how_to_cooke = recipe_soup.find_all('h2', class_='span')
    desc = recipe_soup.find('span', itemprop='recipeInstructions')
    recipe = recipe_soup.find('div', class_='instructions')
    ingredients_ul = recipe_soup.find('ul', class_='detailed_ingredients no_dots')
    description = ''
    recipes = ''
    ingredients_list = []

    if desc:
        for d in desc:
            description += f"{d.text}\n"

    if recipe:
        recipe = recipe.find_all('div', class_='detailed_step_description_big')
        for r in recipe:
            recipes += f"• {r.text}\n\n"

    if ingredients_ul:
        for li in ingredients_ul.find_all('li', itemprop='recipeIngredient'):
            ingredient_name = li.find('span', class_='name').text.strip()
            ingredient_value = li.find('span', class_='value')
            ingredient_unit = li.find('span', class_='u-unit-name').text.strip()

            if ingredient_value:
                ingredient_value_text = ingredient_value.text.strip()
            else:
                ingredient_value_text = ""

            ingredient = f"{ingredient_name}: {ingredient_value_text} {ingredient_unit}"
            ingredients_list.append(ingredient)

        ingredients_text = "\n".join(ingredients_list)

    message_text = (
        f"\n\n<b>Состав/Ингридиенты: 🍎</b>\n\n"
        f"<i>{ingredients_text}</i>\n"
        f"<b>\n{how_to_cooke[0].text} 🍽</b>\n\n"
        f"<i>{recipes}</i>")

    message_text_2 = (
        f"\n\n<b>Состав/Ингридиенты: 🍎</b>\n\n"
        f"{ingredients_text}\n\n"
        f"<b>Описание приготовления: 🍽</b>\n\n{description}")

    if len(how_to_cooke) > 2:
        await bot.send_message(callback_query.from_user.id, message_text, parse_mode='html')
    else:
        await bot.send_message(callback_query.from_user.id, message_text_2, parse_mode='html')


@dp.callback_query_handler(lambda query: query.data.startswith("category:"))
async def show_dishes_for_category(callback_query: types.CallbackQuery):
    selected_category = callback_query.data.split(":")[1]

    category_dishes = parse_category_dishes().get(selected_category, [])

    dishes_keyboard = InlineKeyboardMarkup(row_width=2)

    for dish in category_dishes:
        dishes_keyboard.add(InlineKeyboardButton(text=dish, callback_data=f'dish:{dish}'))

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"Выберите блюдо из категории:",
        reply_markup=dishes_keyboard
    )


@dp.callback_query_handler(lambda query: query.data.startswith("dish:"))
async def send_dish_to_chat(callback_query: types.CallbackQuery):
    selected_dish = callback_query.data.split(":")[1]

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=selected_dish
    )
    await parser_dishes(types.Message(text=selected_dish, chat=callback_query.message.chat))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
