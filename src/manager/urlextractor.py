from typing import Literal
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger

from .requesteng import RequestEngine
from ..core.entites.schemas import MiniHentaiModel

class URLExtractor:
    TOP_URL: Literal["hentai_top.html"] = "hentai_top.html"
    TOP_RATING: Literal["hentai_top100_rating.html"] = "hentai_top100_rating.html"
    
    def __init__(self, engine: RequestEngine, *, features: str = 'html.parser', mirror: str = 'https://anihidew.org'):
        self.engine = engine
        self.features = features
        self.mirror = mirror
        
    async def extract_top(self):
        url = self._urljoin(self.TOP_URL)
        response = await self.engine.request(url, 'text')
        if not response:
            logger.error(f"Не удалось извлечь URL-ы (url={url})")
            return
        
        soup = BeautifulSoup(response, self.features)
        return self._extract_rating_page(soup)
    
    async def extract_top_rating(self):
        url = self._urljoin(self.TOP_RATING)
        response = await self.engine.request(url, 'text')
        if not response:
            logger.error(f"Не удалось извлечь URL-ы (url={url})")
            return
        
        soup = BeautifulSoup(response, self.features)
        return self._extract_rating_page(soup)
        
    def _urljoin(self, url: str) -> str:
        return urljoin(self.mirror, url)
    
    def _extract_rating_page(self, soup: BeautifulSoup) -> list[MiniHentaiModel]:
        result: list[MiniHentaiModel] = []
        for hentai in soup.select('div.sect__content.d-grid a.poster'):
            title = hentai.select_one('h3')
            poster = hentai.select_one('img')
            url = hentai.get('href')
            rating = soup.select_one('div.poster__rating')
            
            if all([title, poster, url, rating]):
                result.append(
                    MiniHentaiModel(
                        title = title.get_text(strip=True), 
                        poster = self._urljoin(poster.get('src')), 
                        url = self._urljoin(url),
                        rating = rating.get_text(strip=True)
                    )
                )
        return result