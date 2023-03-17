import requests
import json

from config import currency


class APIException(Exception):
    """ Общий класс исключений. """
    pass


class Converter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        """ Статический метод который будет конвертировать наши валюты.
        Принимает три аргумента и возвращающий нужную сумму в требуемой валюте.
        Подымаем исключения при ошибочном вводе данных, пользователем."""
        if quote == base:
            raise APIException(f'{base}, не переводится в {base}.')

        try:
            quote_ticker = currency[quote]
        except KeyError:
            raise APIException(f'Валюта {quote}, указана не верно.')

        try:
            base_ticker = currency[base]
        except KeyError:
            raise APIException(f'Валюта {base}, указана не верно.')

        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            raise APIException(f'Количество валюты, {amount}, не допустимо.')

        # Выполняем запрос, передав - (fsym) - какую валюту хотим купить. (tsyms) - за какую валюту мы будем покупать
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')

        total_base = json.loads(r.content)[currency[base]] * amount

        return round(total_base, 2)
