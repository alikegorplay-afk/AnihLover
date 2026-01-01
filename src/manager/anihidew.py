"""Менеджер для сайт anihidew.org актуален на момент 2025-01-01"""

import aiohttp

from loguru import logger

from ..core.entites.schemas import PreviewHentaiModel, M3U8Response
from ..parser import DubingParser, HentaiParser
from .requesteng import RequestEngine
from .downloader import DownloadManager

class Anihidew:
    """Основной менеджер для получение данных"""
    
    def __init__(
        self, 
        session: aiohttp.ClientSession, 
        *, 
        max_try: int = 3, 
        max_concurents: int = 5,
        mirror: str = "https://anihidew.org", 
        features: str = "html.parser",
        
        max_workers: int = 5
    ):
        """Логика, API, нужен для получение информации об сайте

        Args:
            session (aiohttp.ClientSession): Экземпляр aiohttp.ClientSession.
            max_try (int, optional): Максимальное количество попыток. Базовое значение 3.
            max_concurents (int, optional): Максимальное количество запросов. Базовое значение 5.
            mirror (_type_, optional): Домен к сайту. Базовое значение "https://anihidew.org".
            features (str, optional): Особенности при парсинге. Базовое значение "html.parser".
            max_workers (int, optional): Максимальное количество работников во время сборки видео. Базовое значение 5

        Raises:
            TypeError: Если переданный session, не является экземпляром aiohttp.ClientSession
            ValueError: Если максимальное количество попыток, запросов меншье нуля
        """
        self.session = session
        self.mirror = mirror
        self.features = features
        self.max_try = max_try
        self.max_concurents = max_concurents
        
        self.http = RequestEngine(self.session, self.max_try, self.max_concurents)
        
        self.hentai_parser = HentaiParser(self.mirror, self.features)
        self.dubbing_parser = DubingParser(self.mirror, self.features)
        self.downloader = DownloadManager(self.http, max_workers)
        
    async def get_hentai(self, url: str) -> PreviewHentaiModel | None:
        """Получить всю информацию об хентае

        Args:
            url (str): URL - к хентаю

        Returns:
            PreviewHentaiModel | None: Полная информация об хентае.
            
        Example:
            >>> async with aiohttp.ClientSession() as session:
            >>>     api = Anihidew(session)
            >>>     data = await api.get_hentai("https://anihidew.org/1597-guilty-hole.html")
            >>>     print(data)
        """
        response = await self.http.request(url, 'text')
        if response is None:
            logger.warning(f"Не удалось получить хентай (url={url})")
            return

        return self.hentai_parser.extract(response)
    
    async def get_ifrmae(self, url: str) -> M3U8Response | None:
        """Получить все M3u8 из ifrmae

        Args:
            url (str): URL к iframe

        Returns:
            M3U8Response | None: Все M3U8 из iframe если все успешно, иначе None
        """
        response = await self.http.request(url, 'text', self.http._iframe_headers())
        if response is None:
            logger.warning(f"Не удалось получить iframe (url={url})")
            return
        
        
        return self.dubbing_parser.extract(response)
    
    async def get_m3u8(self, url: str) -> str | None:
        """Просто получает m3u8

        Args:
            url (str): Путь к m3u8

        Returns:
            str | None: Исходный текст m3u8 если все успешно, иначе None
        """
        response = await self.http.request(url, 'text', self.http._m3u8_headers())
        if response is None:
            logger.warning(f"Не удалось получить m3u8 (url={url})")
            return
        
        return response
    
    async def download_hentai(self, url: str, path: str = "video.mp4") -> None:
        """Скачать мангу используя M3U8

        Args:
            url (str): URL - к M3U8
            path (str, optional): Путь к файлу для скачивание. Базовое значение "video.mp4".
        """
        await self.downloader.download(url, path)