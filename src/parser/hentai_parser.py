from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from bs4 import BeautifulSoup

from .base import BaseHentaiParser


class HentaiParser(BaseHentaiParser):
    
    def _extract_title(self, soup: BeautifulSoup):
        if title := soup.select_one('h1'):
            return title.get_text(strip=True)
        
        raise self._raise_not_found('title')        
    
    def _extract_url(self, soup: BeautifulSoup):
        if url := soup.select_one('link[rel="canonical"]'):
            return url.get('href')
        
        raise self._raise_not_found('url')
    
    def _extract_poster(self, soup: BeautifulSoup):
        if (poster := soup.select_one('div.pmovie__poster img')) and (url := poster.get('data-src')):
            return self._urljoin(url)
        
        raise self._raise_not_found('poster')
    
    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        if rating := soup.select_one('div.card__rating-ext-count.centered-content'):
            return float(rating.get_text(strip=True))
    
    def _extract_director(self, soup: BeautifulSoup):
        if directors := self._extract_headers(soup).get('Режиссер'):
            return self._correct_headers(directors)
        return []
        
    def _extract_premiere(self, soup: BeautifulSoup):
        return self._extract_headers(soup).get('Премьера', [None])[0]

    def _extract_studio(self, soup: BeautifulSoup):
        if studios := self._extract_headers(soup).get('Студия'):
            return self._correct_headers(studios)
        return []

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
        for li in soup.select('ul[class*="pmovie__header-list"] li'):
            try:
                title, value = li.get_text(strip=True).split(":", 1)
            except ValueError:
                continue
            
            result[title].append(value.strip())
            
        return result
        
    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        if description := soup.select_one('div.page__text'):
            return description.get_text(strip=True)
        
    def _extract_all_iframe(self, soup: BeautifulSoup) -> list[str]:
        urls: list[str] = []
        for iframe in soup.select('div.video-responsive iframe'):
            urls.append(iframe.get('src'))
        return urls