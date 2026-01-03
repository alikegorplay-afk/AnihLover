import asyncio
import sys

import aiohttp

from loguru import logger

from src.manager.sqlmanager import DataBaseManager
from src.manager.anihidew import Anihidew
from src.manager.requesteng import RequestEngine
from src.manager.urlextractor import URLExtractor
from src.core import config

logger.remove()
logger.add(sys.stdout, format = "<red>ANILOVER</red> | <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>")

async def main(engine: RequestEngine, manager: DataBaseManager):
    
    urlextractor = URLExtractor(engine)
    api = Anihidew(engine)
    
    for page in range(1, 136):
        tasks = [asyncio.create_task(api.get_hentai(hentai))
        for hentai in await urlextractor.extract_page(page)]
        
        for task in asyncio.as_completed(tasks):
            hentai = await task
            
            if hentai:
                await manager.add(hentai)

async def init():
    async with aiohttp.ClientSession(
        #**config.proxy
    ) as session:
            
        engine = None
        engine = RequestEngine(session)
        
        try:
            manager = await DataBaseManager.create_manager(config.BD_URL)
            await main(
                engine = engine,
                manager = manager
            )
            
        except Exception as e:
            raise
        
        finally:
            if engine is not None:
                await manager.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(init())
        
    except KeyboardInterrupt:
        logger.info("Процесс остановлен пользавотелем")
    
    finally:
        logger.info("Программа остоновлена")