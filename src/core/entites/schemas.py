from typing import List, Dict
from pydantic import BaseModel, HttpUrl

class MiniHentaiModel(BaseModel):
    """Минимальная модель хентая"""
    title: str
    url: HttpUrl
    poster: HttpUrl
    rating: float | None = None

    @property
    def id(self) -> int:
        return int(self.url.encoded_string().split('/')[-1].split('-')[0])

class FindHentaiModel(MiniHentaiModel):
    premiere: str | None = None
    status: str | None = None
    
    voiceover: List[str] | None = None
    subtitles: List[str] | None = None
    genres: List[str] | None = None
    description: str | None = None

class BaseHentaiModel(MiniHentaiModel):
    """Базовая модель хентая"""
    
    director: list[str] | None = None
    premiere: str | None = None
    studio: list[str] | None = None
    status: str | None = None
    
    voiceover: List[str] | None = None
    subtitles: List[str] | None = None
    genres: List[str] | None = None
    description: str | None = None
    
class HentaiModel(BaseHentaiModel):
    all_m3u8: Dict[str, HttpUrl]
    
class PreviewHentaiModel(BaseHentaiModel):
    all_iframe: List[HttpUrl]

class M3U8Prewiev(BaseModel):
    number: int
    title: str
    url: HttpUrl
    poster: HttpUrl
    thumbnail: HttpUrl
    
class M3U8Response(BaseModel):
    dub_name: str
    all_m3u8: List[M3U8Prewiev]