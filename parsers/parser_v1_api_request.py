from datetime import datetime

import requests

from database import index_db
from models import IndexDataPoint
from parsers.base_parser import BaseParser


class IndexAPIParser(BaseParser):
    """
    Класс для парсинга индексов с сайта tbank.ru/invest/indexes.
    Получает исторические данные по индексу за указанный период.
    """

    def __init__(self, index: str, period: str = 'year'):
        """
        Инициализация парсера.

        :param index: Название индекса.
        :param period: Период данных (доступны 'all' и 'year').
        """
        self.index = index
        self.api_url = f'https://www.tbank.ru/api/invest-gw/capital/funds/v1/indexes/{index}/history?period={period}'

    def get_data(self, last: int = 0) -> list[IndexDataPoint]:
        """
        Получает данные по индексу с API.

        :param last: Количество последних записей, которые нужно вернуть. Если 0, возвращает все данные.
        :return: Список объектов IndexDataPoint.
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка запроса к API: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Ошибка парсинга JSON: {e}") from e

        try:
            result = [IndexDataPoint(datetime.fromisoformat(point['dateTime']), point['value']) for point in
                      data['payload']['index']]
        except (KeyError, TypeError, ValueError) as e:
            raise RuntimeError(f"Ошибка обработки данных API: {e}") from e

        return result[-last:] if last and last <= len(result) else result

    def save_to_db(self, last: int = 0):
        """
        Сохраняет данные индекса в базу данных.

        :param last: Количество последних записей, которые нужно записать в БД. Если 0, записывает все данные.
        """
        data_points = self.get_data(last)
        if data_points:
            index_db.save_index_data(index_name=self.index, data_points=data_points)
        else:
            raise RuntimeError("Нет данных для сохранения в базу.")
