from abc import abstractmethod


class BaseDatabase:
    _init = False

    @abstractmethod
    async def get_connection(self):
        """Получить коннект к базе данных"""

    @abstractmethod
    async def close_connection(self):
        """Закрытие всех соединений"""

    @abstractmethod
    def init(self):
        """Инициализация"""
