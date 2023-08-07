import requests
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API
from bs4 import BeautifulSoup

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
        url = 'https://povar.ru/' + link.find('div', class_='h3').find('a', class_='listRecipieTitle').get('href')
        name = link.find('div', class_='h3').find('a', class_='listRecipieTitle').text
        description = link.find('p', class_='txt').text
        image = link.find('span', class_='a thumb hashString').find('img').get('src')
        await bot.send_photo(message.chat.id, image, "<b>" + name + "</b>\n<i>" + description + f"</i>\n<a href='{url}'>Посмотреть подробнее</a>", parse_mode='html')


if __name__ == '__main__':
    executor.start_polling(dp)