import telebot
import requests
import json

# создаем константу (TOKEN) и присваиваем токен нашего бота, созданного https://t.me/BotFather
TOKEN = '6255381998:AAF-NNi212IdsDsyAXZh-wUpdWZE3gHZtxA'

# создаем словарь с валютами, которые будут доступны для конвертации
currency = {'рубль': 'RUB',
            'доллар': 'USD',
            'евро': 'EUR',
            'юань': 'CNY',
            'драм': 'AMD',
            'лари': 'GEL',
            'йена': 'JPY',
            'тенге': 'KZT',
            'биткоин': 'BTC',
            'эфириум': 'ETH',
            'тезер': 'USDT'}

# Создаем объект (bot) класса TeleBot и передаем ему в конструктор наш TOKEN
bot = telebot.TeleBot(TOKEN)


class APIException(Exception):
    """ Общий класс исключений. """
    pass


class Converter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        """ Статический метод который будет конвертировать наши валюты.
        Принимает три аргумента и возвращающий нужную сумму в требуемой валюте.
        Подымаем исключения при ошибочном вводе данных, пользователем."""
        if quote == base:  # если запрошены одинаковые валюты, подымаем исключение
            raise APIException(f'{base}, не переводится в {base}.')

        try:
            # переменной, присваиваем значение валюты из словаря (currency) и затем подставляем в (get) запрос.
            quote_ticker = currency[quote]
        except KeyError:  # если при вводе указана валюта отсутствующая в словаре, подымаем исключение
            raise APIException(f'Валюта {quote}, указана не верно.')

        try:
            base_ticker = currency[base]
        except KeyError:
            raise APIException(f'Валюта {base}, указана не верно.')

        try:
            # если при вводе количества валюты, указана (,), то меняем её на (.) и строку преобразуем в тип данных float
            amount = float(amount.replace(',', '.'))
        except ValueError:  # если введено не число, подымаем исключение
            raise APIException(f'Количество валюты, {amount}, не допустимо.')

        # Выполняем запрос, передав - (fsym) - какую валюту хотим купить. (tsyms) - за какую валюту мы будем покупать
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')

        # полученный ответ умножаем на количество и записываем в переменную
        total_base = json.loads(r.content)[currency[base]] * amount

        return round(total_base, 2)  # возврат значения после конвертации, округленную до 2 знаков после запятой


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
    for key in currency.keys():         # пройдемся по ключам (keys) валют из нашего славоря (currency)
        text = '\n'.join((text, key,))  # будем выводить каждый ключ с новой строки
    bot.reply_to(message, text)         # и отвечаем на сообщение


# декоратор отлавливающие ввод от пользователя и обработчик.
@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        accept = message.text.lower().split()  # принятые данные приводим к малому регистру и делим на значения
        if len(accept) != 3:                   # если значений не 3, то поднимаем исключение
            raise APIException('Не верное количество параметров.')

        quote, base, amount = accept  # полученным значениям, присваиваем переменные
        total_base = Converter.get_price(quote, base, amount)  # получаем итоговое значение из класса Converter

    except APIException as e:  # сообщение об ошибке возникшей из-за действий пользователя.
        bot.reply_to(message, f'Ошибка ввода.\n{e}')

    except Exception as e:  # сообщение об ошибке не по вине пользователя.
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')

    else:  # при отсутствии ошибок, получаем результат конвертации
        text = f'Цена {amount} {quote} в {base} = {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
