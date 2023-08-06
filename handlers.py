from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Здравствуйте! Напишите название блюда, которое хотели бы найти')
    await message.delete()

if __name__ == '__main__':
    executor.start_polling(dp)