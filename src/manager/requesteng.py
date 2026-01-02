"""Менеджер для запросов"""

import asyncio
from typing import Literal, overload

import aiohttp

from loguru import logger

class RequestEngine:
    """Логика запросов"""
    
    def __init__(self, session: aiohttp.ClientSession, max_try: int = 3, max_concurents: int = 5):
        """Логика запросов, прямой HTTP.

        Args:
            session (aiohttp.ClientSession): Экземпляр aiohttp.ClientSession.
            max_try (int, optional): Максимальное количество попыток. Базовое значение 3.
            max_concurents (int, optional): Максимальное количество запросов. Базовое значение 5.

        Raises:
            TypeError: Если переданный session, не является экземпляром aiohttp.ClientSession
            ValueError: Если максимальное количество попыток, запросов меншье нуля
        """
        self.session = session
        self.max_try = max_try
        self.max_concurents = max_concurents
        
        if not isinstance(self.session, aiohttp.ClientSession):
            raise TypeError(
                "Параметр session должен быть экземпляром aiohttp.ClientSession"
            )
        if self.max_try <= 0 or self.max_concurents <= 0:
            raise ValueError(
                "Максимальное количество попыток и одновременных запросов должно быть больше 0"
            )
            
        self.semaphore = asyncio.Semaphore(self.max_concurents)

    @overload
    async def request(self, url: str, response_type: Literal["text"], headers: dict[str, str] = {}) -> str | None: ...
    @overload
    async def request(self, url: str, response_type: Literal["bytes"], headers: dict[str, str] = {}) -> bytes | None: ...
    
    async def request(self, url: str, response_type: Literal["text", "bytes"] = "text", headers: dict[str, str] = {}) -> str | bytes | None:
        """Главная функция для получения данных

        Args:
            url (str): URL путь к ресурсу
            response_type (Literal["text", "bytes"], optional): Тип возращаемых данных. Базовое значение "text".

        Returns:
            str | bytes | None: str если response_type "text", bytes если response_type "bytes" если данные не удалось получить None
        """
        async with self.semaphore:
            for index in range(1, self.max_try + 1):
                logger.debug(f"Попытка получить данные (url={url}, try-num={index})")
                try:
                    async with self.session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        if response_type == 'text':
                            return await response.text()
                        else:
                            return await response.read()
                        
                except aiohttp.ClientResponseError as e:
                    if e.status == 404:
                        logger.error(f"Страница не найдена (status={e.status}, url={url})")
                        return
                    
                    elif e.status == 403:
                        logger.error(f"Не удалось получить данные, возможно страница не доступна гостям (status={e.status}, url={url})")
                        return
                    
                    else:
                        logger.warning(f"Не удалось получить данные (status={e.status}, url={url})")
                        
                except Exception as e:
                    logger.error(f"Неизвестная ошибка (error={e})")
                    
        return None
        
    def _iframe_headers(self) -> dict[str, str]:
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ru,en;q=0.9',
            'referer': 'https://anihidew.org/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36',
        }
        
    def _m3u8_headers(self) -> dict[str, str]:
        return {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': 'https://ifr.animecrows.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "YaBrowser";v="25.12", "Not_A Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
        }