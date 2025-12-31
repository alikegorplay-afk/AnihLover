import os
from dataclasses import dataclass

@dataclass
class Config:
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