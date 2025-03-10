import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from database import index_db
from models import IndexDataPoint
from parsers.base_parser import BaseParser


class IndexRequestsParser(BaseParser):
    """
    Парсер индексов с сайта tbank.ru/invest/indexes с использованием Requests.
    """

    def __init__(self, index: str, period: str = 'year'):
        """
        Инициализация парсера.

        :param index: Название индекса.
        :param period: Период данных (доступны 'all' и 'year').
        """
        self.index = index.upper()
        self.period = period.lower()
        self.url = f'https://www.tbank.ru/invest/indexes/{index}/'
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

    def get_data(self, last: int = 0) -> list[IndexDataPoint]:
        """
        Получает данные по индексу с HTML страницы.

        :param last: Количество последних записей, которые нужно вернуть. Если 0, возвращает все данные.
        :return: Список объектов IndexDataPoint.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Находим тег <script>, содержащий JSON
            script_tag = soup.find("script", id="__TRAMVAI_STATE__")
            if not script_tag:
                raise ValueError("JSON-данные не найдены в HTML-коде.")

            # Извлекаем текст из тега
            json_data = script_tag.string

            # Преобразуем JSON-строку в словарь
            data = json.loads(json_data)

        except Exception as e:
            raise RuntimeError(f"Ошибка: {e}") from e

        try:
            index_data = data['stores']["investIndexHistory"][self.index]
            if index_data.get(self.period, None):
                result = [IndexDataPoint(datetime.fromisoformat(point['dateTime']), point['value']) for point in
                          index_data[self.period]["index"]]
            else:
                result = [IndexDataPoint(datetime.fromisoformat(point['dateTime']), point['value']) for point in
                          index_data['year']["index"]]
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
