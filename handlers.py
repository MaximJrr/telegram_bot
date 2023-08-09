import requests
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API
from bs4 import BeautifulSoup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Здравствуйте! Напишите название блюда, которое хотели бы найти')
    await message.delete()


@dp.message_handler(content_types=['text'])
async def parser_dishes(message: types.Message):
    url = "https://povar.ru/xmlsearch?query=" + message.text
    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    links = soup.find_all('div', class_='recipe')

    for link in links:
        recipe_id = link.find('div', class_='h3').find('a', class_='listRecipieTitle').get('href').split("-")[-1].split(".")[0]

        inline_button = InlineKeyboardButton("Посмотреть подробнее", callback_data=f"recipe:{recipe_id}")
        inline_markup = InlineKeyboardMarkup().add(inline_button)

        name = link.find('div', class_='h3').find('a', class_='listRecipieTitle').text
        description = link.find('p', class_='txt').text
        image = link.find('span', class_='a thumb hashString').find('img').get('src')

        await bot.send_photo(
            message.chat.id,
            image,
            f"*{name}*\n_{description}_",
            reply_markup=inline_markup,
            parse_mode='markdown'
        )


@dp.callback_query_handler(lambda query: query.data.startswith("recipe:"))
async def get_recipe_details(callback_query: types.CallbackQuery):
    recipe_id = callback_query.data.split(":")[1]
    recipe_url = f"https://povar.ru/recipes/picca_v_domashnih_usloviyah_v_duhovke-{recipe_id}.html"

    recipe_request = requests.get(recipe_url)
    recipe_soup = BeautifulSoup(recipe_request.text, "html.parser")

    description = recipe_soup.find(
        'span', class_='detailed_full description').find_next('br').find_next_sibling('span').text.strip()

    await bot.send_message(callback_query.from_user.id, description)

if __name__ == '__main__':
    executor.start_polling(dp)
