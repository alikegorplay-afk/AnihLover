from collections import defaultdict

from bs4 import BeautifulSoup, _IncomingMarkup
from functools import lru_cache

from .base import BaseParser
from ..core.entites.schemas import FindHentaiModel

class PageParser(BaseParser):
    def extract(self, markup: _IncomingMarkup):
        result = []
        if isinstance(markup, BeautifulSoup):
            soup = markup
        else:
            soup = BeautifulSoup(markup, self.features)
            
        for card in soup.select("div#dle-content article.card"):
            title = self._extract_title(card)
            url = self._extract_url(card)
            poster = self._extract_poster(card)
            rating = self._extract_rating(card)
            
            premiere = self._extract_premiere(card)
            status = self._extract_status(card)
            
            voiceover = self._extract_voiceover(card)
            subtitles = self._extract_subtitles(card)
            genres = self._extract_genres(card)
            
            description = self._extract_description(card)
            
            result.append(
                FindHentaiModel(
                title = title,
                url = url,
                poster = poster,
                rating = rating,
                premiere = premiere,
                status = status,
                voiceover = voiceover,
                subtitles = subtitles,
                genres = genres,
                description = description
            )
            )
        return result
            
    def _extract_title(self, soup: BeautifulSoup) -> str:
        if title := soup.select_one('h2.card__title'):
            return title.get_text(strip=True)
        self._raise_not_found('title')
        
    def _extract_url(self, soup: BeautifulSoup) -> str:
        if url := soup.select_one('a'):
            return self._urljoin(url.get('href'))
        self._raise_not_found('url')
        
    def _extract_poster(self, soup: BeautifulSoup) -> str:
        if poster := soup.select_one('img'):
            return self._urljoin(poster.get('src'))
        self._raise_not_found('poster')
        
    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        if rating := soup.select_one('div.card__rating-ext-count'):
            return float(rating.get_text(strip=True))
        return None
        
    def _extract_premiere(self, soup: BeautifulSoup):
        return self._extract_headers(soup).get('Премьера', [None])[0]

    def _extract_status(self, soup: BeautifulSoup):
        return self._extract_headers(soup).get('Статус', [None])[0]
        
    def _extract_voiceover(self, soup: BeautifulSoup):
        return self._correct_headers(self._extract_headers(soup).get('Озвучка', []))
        
    def _extract_subtitles(self, soup: BeautifulSoup):
        return self._correct_headers(self._extract_headers(soup).get('Субтитры', []))
        
    def _extract_genres(self, soup: BeautifulSoup):
        if genres := self._extract_headers(soup).get('Жанр'):
            if " / " in genres[0]:
                return genres[0].split(" / ")
            else:
                return genres[0].split(", ")
        return []
    
    @lru_cache(1)
    def _extract_headers(self, soup: BeautifulSoup) -> dict[str, list[str]]:
        result = defaultdict(list)
        if headers := soup.select_one('ul.card__list'):
            result = defaultdict(list)
            for li in headers.select('li'):
                try:
                    title, value = li.get_text(strip=True).split(":", 1)
                except ValueError:
                    continue
                result[title].append(value.strip())
        return result
        
    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        if description := soup.select_one('p.card__text'):
            return description.get_text(strip=True)
        return None