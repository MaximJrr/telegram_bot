import telebot
from telebot.types import Message
from config import TOKEN_API

bot = telebot.TeleBot(TOKEN_API)


@bot.message_handler(commands=['start'])
def start_command(message: Message):
    bot.send_message(message.chat.id, text='Здравствуйте! Напишите название блюда, которое хотели бы найти')
    bot.delete_message(message.chat.id, message.id)


if __name__ == '__main__':
    bot.polling()