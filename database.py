from datetime import datetime

import mysql.connector
from mysql.connector import Error

from config import settings
from models import IndexDataPoint


class IndexRepository:
    @staticmethod
    def _create_connection():
        """Создает соединение с базой данных."""
        try:
            connection = mysql.connector.connect(**settings.database_config_dict)
            return connection
        except Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def _ensure_table_exists(self, index_name: str):
        """
        Проверяет, существует ли таблица для указанного индекса. Если нет — создает её.
        :param index_name: Название индекса (например, 'TIPOUS').
        """
        with self._create_connection() as connection:
            cursor = connection.cursor()
            table_name = index_name.upper()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    value FLOAT NOT NULL,
                    UNIQUE KEY unique_timestamp_value (timestamp, value)
                )
            """)
            connection.commit()
            cursor.close()

    def save_index_data(self, index_name: str, data_points: list[IndexDataPoint]):
        """
        Сохраняет данные индекса в базу данных.
        :param index_name: Название индекса (например, 'TIPOUS').
        :param data_points: Список объектов IndexDataPoint.
        """
        self._ensure_table_exists(index_name)
        with self._create_connection() as connection:
            cursor = connection.cursor()
            table_name = index_name.upper()

            query = f"""
                        INSERT IGNORE INTO {table_name} (timestamp, value)
                        VALUES (%s, %s)
                    """

            values = [
                (point.timestamp.replace(microsecond=0), point.value)
                for point in data_points
            ]

            cursor.executemany(query, values)
            connection.commit()
            cursor.close()

    def get_index_data(self, index_name: str, start_date: datetime = None, end_date: datetime = None) -> list[
        IndexDataPoint]:
        """
        Получает данные индекса из базы данных.
        :param index_name: Название индекса (например, 'TIPOUS').
        :param start_date: Начальная дата для фильтрации (опционально).
        :param end_date: Конечная дата для фильтрации (опционально).
        :return: Список объектов IndexDataPoint.
        """
        self._ensure_table_exists(index_name)
        with self._create_connection() as connection:
            cursor = connection.cursor()
            table_name = index_name.upper()

            query = f"SELECT timestamp, value FROM {table_name}"
            conditions = []
            if start_date:
                conditions.append(f"timestamp >= '{start_date}'")
            if end_date:
                conditions.append(f"timestamp <= '{end_date}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return [IndexDataPoint(timestamp=row[0], value=row[1]) for row in results]


index_db = IndexRepository()

if __name__ == '__main__':
    index_db._ensure_table_exists('tipous_test')
