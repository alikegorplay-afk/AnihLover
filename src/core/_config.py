import os
import aiohttp
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class ProxyConfig:
    _proxy = os.getenv("PROXY", None) # Писать в виде http://ip:port
    _proxy_auth = os.getenv("PROXY_AUTH", None) # Писать в виде логин:пароль

    @property
    def proxy(self):
        if self._proxy:
            return {
                "proxy": self._proxy,
                'proxy_auth': aiohttp.BasicAuth(self._proxy_auth.split(':')[0], self._proxy_auth.split(':')[1]) if self._proxy_auth else None
            }
        else:
            return {}
        

@dataclass
class Config(
    ProxyConfig
):
    BD_URL: str = os.getenv("DB_URL", "sqlite+aiosqlite:///database.db")
    """Путь к базе данных"""
    
    features: str = 'html.parser'
    """Базовый парсер"""
    
    interval: float = 300
    """Базовый интервал перед следующим парсингом. Базовое значение 300 секнуд (5 минут)"""
    
    def __post_init__(self):
        if not self.BD_URL:
            raise ValueError(
                "Не определён DB_URL, пожалуйста проверьте ваш путь"
            )
        
        if self.interval < 0:
            raise ValueError(
                "Интервал между запросами не может быть отрицательным"
            )
            
config = Config()