from abc import ABC, abstractmethod
from models import IndexDataPoint


class BaseParser(ABC):
    """Базовый класс для всех парсеров индексов."""

    @abstractmethod
    def get_data(self) -> list[IndexDataPoint]:
        """Метод для парсинга данных. Должен быть реализован в дочерних классах."""
        pass

    @abstractmethod
    def save_to_db(self) -> None:
        pass
