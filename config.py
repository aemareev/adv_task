import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    @property
    def database_config_dict(self) -> dict[str, str]:
        """Возвращает словарь для подключения к БД"""
        return {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'database': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASS,
        }

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), ".env"))


# Создаём экземпляр настроек, чтобы использовать в приложении
settings = Settings()

if __name__ == '__main__':
    print(settings.database_config_dict)
