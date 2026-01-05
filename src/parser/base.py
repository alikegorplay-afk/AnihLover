from urllib.parse import urljoin
from abc import ABC, abstractmethod
from typing import Any

from bs4 import _IncomingMarkup, BeautifulSoup

from ..core.entites.schemas import PreviewHentaiModel
from .errors import RequiredAttributeNotFound

class BaseParser(ABC):
    """Базовый парсер"""
    def __init__(self, base_url: str, features: str = 'html.parser'):
        self.base_url = base_url
        self.features = features
        
    @abstractmethod
    def extract(self, markup: _IncomingMarkup) ->Any:
        """Главный метод для извлечение данных

        Args:
            markup (_IncomingMarkup): Поддерживаемый формат данных BS4
        """
        
    def _urljoin(self, url: str) -> str:
        return urljoin(self.base_url, url)
    
    def _raise_not_found(self, message: str) -> None:
        raise RequiredAttributeNotFound(f'Обязательный атрибут "{message}" не обнаружен')
    
    def _correct_headers(self, items: list[str]) -> list[str]:
        result = []
        for item in items:
            item = item.replace(", ", " & ")
            if " & " in item:
                result.extend(x.strip() for x in item.split(" & "))
            else:
                result.append(item.strip())
        
        return result
    
class BaseHentaiParser(BaseParser):
    """Базовый класс для парсинга хентая"""
    
    def extract(self, markup: _IncomingMarkup) -> PreviewHentaiModel:
        soup = BeautifulSoup(markup, self.features)
        
        title = self._extract_title(soup)
        url = self._extract_url(soup)
        poster = self._extract_poster(soup)
        rating = self._extract_rating(soup)
        
        director = self._extract_director(soup)
        premiere = self._extract_premiere(soup)
        studio = self._extract_studio(soup)
        status = self._extract_status(soup)
        
        voiceover = self._extract_voiceover(soup)
        subtitles = self._extract_subtitles(soup)
        genres = self._extract_genres(soup)
        
        description = self._extract_description(soup)
        all_iframe = self._extract_all_iframe(soup)
        
        return PreviewHentaiModel(
            title = title,
            url = url,
            poster = poster,
            rating = rating,
            director = director,
            premiere = premiere,
            studio = studio,
            status = status,
            voiceover = voiceover,
            subtitles = subtitles,
            genres = genres,
            description = description,
            all_iframe = all_iframe
        )
        
    @abstractmethod
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Извлечение название"""      
    
    @abstractmethod
    def _extract_url(self, soup: BeautifulSoup) -> str:
        """Извлечение url"""
    
    @abstractmethod
    def _extract_poster(self, soup: BeautifulSoup) -> str:
        """Извлечение постера"""
    
    @abstractmethod
    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        """Извлечение рейтинга"""
    
    @abstractmethod
    def _extract_director(self, soup: BeautifulSoup) -> list[str]:
        """Извлечение режиссера"""
        
    @abstractmethod
    def _extract_premiere(self, soup: BeautifulSoup) -> str:
        """Извлечение премьеры"""

    @abstractmethod
    def _extract_studio(self, soup: BeautifulSoup) -> list[str]:
        """Извлечение студии"""

    @abstractmethod
    def _extract_status(self, soup: BeautifulSoup) -> str:
        """Извлечение статуса"""
    
    @abstractmethod
    def _extract_voiceover(self, soup: BeautifulSoup) -> list[str]:
        """Извлечение озвучки"""
    
    @abstractmethod
    def _extract_subtitles(self, soup: BeautifulSoup) -> list[str]:
        """Извлечение субтитров"""
    
    @abstractmethod
    def _extract_genres(self, soup: BeautifulSoup) -> list[str]:
        """Извлечение жанров"""
        
    @abstractmethod
    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        """Извлечение описания"""
        
    @abstractmethod     
    def _extract_all_iframe(self, soup: BeautifulSoup) -> list[str]:
        """Извлечение всех iframe"""