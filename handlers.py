import requests
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API, headers
from bs4 import BeautifulSoup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


async def on_startup(_):
    print("Bot started")


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Здравствуйте! Напишите название блюда, которое хотели бы найти')
    await message.delete()


@dp.message_handler(content_types=['text'])
async def parser_dishes(message: types.Message):
    for page in range(1, 6):
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

            if len(link) == 2:
                break
            else:
                await bot.send_photo(
                    message.chat.id,
                    image,
                    f"*{name}*\n_{description}_",
                    reply_markup=inline_markup,
                    parse_mode='markdown'
                )

    if not dishes_found:
        await bot.send_message(
            message.chat.id, f"К сожалению, блюдо <b>'{message.text}'</b> не найдено 😢", parse_mode='html'
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
    await bot.send_message(callback_query.from_user.id, message_text_2, parse_mode='html')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
