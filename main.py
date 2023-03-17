import telebot

from config import *
from extensions import APIException, Converter

bot = telebot.TeleBot(TOKEN)


# декораторы, отлавливающие команды (start, help, currency) и обработчики.
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = f'Приветствую, {message.chat.username}\n\nОзнакомиться с правилами ввода: /help\n' \
           'Увидеть список всех доступных валют: /currency'
    bot.reply_to(message, text)


@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    text = 'Через пробел введите три параметра:\n\n<переводимая валюта>\n<в какую валюту перевести>\n' \
           '<количество переводимой валюты>\n\nПример: доллар рубль 100'
    bot.reply_to(message, text)


@bot.message_handler(commands=['currency'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for key in currency.keys():
        text = '\n'.join((text, key,))
    bot.reply_to(message, text)


# декоратор отлавливающий ввод от пользователя и обработчик.
@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        accept = message.text.lower().split()
        if len(accept) != 3:
            raise APIException('Не верное количество параметров.')

        quote, base, amount = accept
        total_base = Converter.get_price(quote, base, amount)

    except APIException as e:
        bot.reply_to(message, f'Ошибка ввода.\n{e}')

    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')

    else:
        text = f'Цена {amount} {quote} в {base} = {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
