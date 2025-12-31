from typing import List, Dict
from pydantic import BaseModel, HttpUrl

class HentaiModel(BaseModel):
    title: str
    url: HttpUrl
    poster: HttpUrl
    
    genres: List[str]
    description: str
    
    all_m3u8: Dict[str, HttpUrl]
    
    @property
    def id(self) -> int:
        return int(self.poster.encoded_string().split('/')[-1].split('-')[0])