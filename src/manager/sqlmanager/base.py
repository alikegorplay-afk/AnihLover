from typing import TypedDict
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine, create_async_engine
from loguru import logger

from ...core.entites.schemas import (PreviewHentaiModel)
from ...core.entites.models import (
    Base, 
    Director,
    Studio,
    Voiceover,
    Subtitles,
    Genres,
    Hentai
)

class HentaiDict(TypedDict):
    director: Director | None
    studio: Studio | None
    voiceover: list[Voiceover]
    subtitles: list[Subtitles]
    genres: list[Genres]

class BaseDataBaseManager:
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.Session: async_sessionmaker[AsyncSession] = async_sessionmaker(self.engine)
    
    @classmethod
    async def create_manager(cls, url: str):
        engine = create_async_engine(url)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        return cls(engine)
    
    async def dispose(self):
        await self.engine.dispose()
        
    async def get(self, id: int) -> PreviewHentaiModel | None:
        async with self.Session() as session:
            hentai = await session.get(Hentai, id)
            if hentai is None:
                logger.warning(f"Не найден хентай (id={id})")
                return
            
            return PreviewHentaiModel(
                title = hentai.title,
                url = hentai.url,
                poster = hentai.poster,
                rating = hentai.rating,
                director = hentai.director.name,
                premiere = hentai.premier,
                studio = hentai.studio.name,
                status = hentai.status,
                voiceover = [x.name for x in hentai.voiceovers],
                subtitles = [x.name for x in hentai.subtitles_list],
                genres = [x.name for x in hentai.genres_list],
                description = hentai.description,
                all_iframe = hentai.all_iframe
            )
        
    