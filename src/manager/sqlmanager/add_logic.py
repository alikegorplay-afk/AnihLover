from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from ...core.entites.models import (
    Hentai,
    Director,
    Studio,
    Voiceover,
    Subtitles,
    Genres,
    
    DirectorHentai,
    StudioHentai,
    VoiceoverHentai,
    SubtitlesHentai,
    GenresHentai
)
from ...core.entites.schemas import PreviewHentaiModel
from .base import BaseDataBaseManager, HentaiDict


class AddLogic(BaseDataBaseManager):
    
    async def add(self, model: PreviewHentaiModel):
        async with self.Session() as session:
            if (hentai := await session.get(Hentai, model.id)):
                logger.warning(f"В БД, обнаружен хентай (id={hentai.id}, title={hentai.title})")
                return
            try:
                ids = await self._add_all(session, model)
                
                hentai = Hentai(
                    id = model.id,
                    title = model.title,
                    poster = model.poster.encoded_string(),
                    url = model.url.encoded_string(),
                    rating = model.rating,
                    premier = model.premiere,
                    status = model.status,
                    description = model.description,
                    all_iframe = [x.encoded_string() for x in model.all_iframe]
                )
                
                session.add(hentai)
                await session.flush()
                
                await self._connect_hentai(session, model, ids)
                logger.success(f"Хентай успешно сохранён (id={hentai.id})")
                await session.commit()
                
            except Exception as e:
                logger.error(f"Ошибка при добавлении хентая (error={e})")
                await session.rollback()
                
    async def _connect_hentai(self, session: AsyncSession, model: Hentai, ids: HentaiDict):
        if (directors := ids['director']):
            director_connector = []
            for director in directors:
                director = DirectorHentai(
                    hentai_id = model.id,
                    director_id = director.id
                )
                director_connector.append(director)
            session.add_all(director_connector)
            
        if (studios := ids['studio']):
            studio_connector = []
            for studio in studios:
                std = StudioHentai(
                    hentai_id = model.id,
                    studio_id = studio.id
                )
                studio_connector.append(std)
            session.add_all(studio_connector)
            
        if (voiceover := ids['voiceover']):
            voice_connector = []
            for voice in voiceover:
                voice = VoiceoverHentai(
                    hentai_id = model.id,
                    voiceover_id = voice.id
                )
                voice_connector.append(voice)
            session.add_all(voice_connector)
        
        if (subtitles := ids['subtitles']):
            subtitle_connector = []
            for subtitle in subtitles:
                subtitle = SubtitlesHentai(
                    hentai_id = model.id,
                    subtitles_id = subtitle.id
                )
                subtitle_connector.append(subtitle)
            session.add_all(subtitle_connector)
            
        if (genres := ids['genres']):
            genres_connector = []
            for genre in genres:
                genre = GenresHentai(
                    hentai_id = model.id,
                    genre_id = genre.id
                )
                genres_connector.append(genre)
            session.add_all(genres_connector)
            
    async def _add_all(self, session: AsyncSession, model: PreviewHentaiModel) -> HentaiDict:
        return HentaiDict(
            director = await self._add_director(session, model),
            studio = await self._add_studio(session, model),
            voiceover = await self._add_voiceover(session, model),
            subtitles = await self._add_subtitles(session, model),
            genres = await self._add_genres(session, model)
        )
    
    async def _add_director(self, session: AsyncSession, model: PreviewHentaiModel) -> list[Director]:
        result = []
        if model.director is None:
            return result
        
        for director_name in model.director:
            director = await session.scalar(select(Director).where(Director.name == director_name))
            if director is not None:
                result.append(director)
                continue
        
            director = Director(
                name = director_name
            )
            
            session.add(director)
            await session.flush()
            
            result.append(director)
            
        return result
        
    async def _add_studio(self, session: AsyncSession, model: PreviewHentaiModel) -> list[Studio]:
        result = []
        if model.studio is None:
            return result
        
        for studio_name in model.studio:
            studio = await session.scalar(select(Studio).where(Studio.name == studio_name))
            if studio is not None:
                result.append(studio)
                continue
        
            studio = Studio(
                name = studio_name
            )
            
            session.add(studio)
            await session.flush()
            
            result.append(studio)
            
        return result
    
    async def _add_voiceover(self, session: AsyncSession, model: PreviewHentaiModel) -> list[Voiceover]:
        result = []
        if model.voiceover is None:
            return result
        
        for voiceover_name in model.voiceover:
            voiceover = await session.scalar(select(Voiceover).where(Voiceover.name == voiceover_name))
            if voiceover is not None:
                result.append(voiceover)
                continue
            
            voiceover = Voiceover(
                name = voiceover_name
            )
            
            session.add(voiceover)
            await session.flush()
            
            result.append(voiceover)
        
        return result
    
    async def _add_subtitles(self, session: AsyncSession, model: PreviewHentaiModel) -> list[Subtitles]:
        result = []
        if model.subtitles is None:
                return result
        
        for subtitle_name in model.subtitles:
            subtitle = await session.scalar(select(Subtitles).where(Subtitles.name == subtitle_name))
            if subtitle is not None:
                result.append(subtitle)
                continue
            
            subtitle = Subtitles(
                name = subtitle_name
            )
            
            session.add(subtitle)
            await session.flush()
            
            result.append(subtitle)
            
        return result
    
    async def _add_genres(self, session: AsyncSession, model: PreviewHentaiModel) -> list[Genres]:
        result = []
        if model.genres is None:
                return result
        
        for genre_name in model.genres:
            genre = await session.scalar(select(Genres).where(Genres.name == genre_name))
            if genre is not None:
                result.append(genre)
                continue
            
            genre = Genres(
                name = genre_name
            )
            
            session.add(genre)
            await session.flush()
            
            result.append(genre)
            
        return result