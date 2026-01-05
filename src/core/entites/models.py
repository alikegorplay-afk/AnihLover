from typing import List, Optional
from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, JSON, Text, ForeignKey

__all__ = [
    "Director",
    "Studio",
    "Voiceover",
    "Subtitles",
    "Genres",
    "VoiceoverHentai",
    "SubtitlesHentai",
    "GenresHentai",
    "Hentai",
    "Base"
]

class Base(DeclarativeBase):
    ...

# Сначала объявляем основные классы, на которые будут ссылаться ассоциативные таблицы
class Director(Base):
    __tablename__ = "director"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    
    # Исправлено: должно быть "hentais" (множественное число) и ссылаться на ассоциативную таблицу
    hentais: Mapped[List["Hentai"]] = relationship(
        "DirectorHentai", 
        back_populates="director"
    )
    
    def __repr__(self):
        return "Director(id={}, name='{}')".format(self.id, self.name)

class Studio(Base):
    __tablename__ = "studio"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    
    hentais: Mapped[List["Hentai"]] = relationship(
        "StudioHentai", 
        back_populates="studio"
    )
    
    def __repr__(self):
        return f"Studio(id={self.id}, name='{self.name}')"

class Voiceover(Base):
    __tablename__ = "voiceover"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    
    hentais: Mapped[List["Hentai"]] = relationship(
        "VoiceoverHentai", 
        back_populates="voiceover"
    )
    
    def __repr__(self):
        return f"Voiceover(id={self.id}, name='{self.name}')"
    
class Subtitles(Base):
    __tablename__ = "subtitles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    
    hentais: Mapped[List["Hentai"]] = relationship(
        "SubtitlesHentai", 
        back_populates="subtitles"
    )
    
    def __repr__(self):
        return f"Subtitles(id={self.id}, name='{self.name}')"
    
class Genres(Base):
    __tablename__ = "genres"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    
    hentais: Mapped[List["Hentai"]] = relationship(
        "GenresHentai", 
        back_populates="genre"
    )
    
    def __repr__(self):
        return f"Genres(id={self.id}, name='{self.name}')"

class DirectorHentai(Base):
    __tablename__ = "director_hentai"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    hentai_id: Mapped[int] = mapped_column(ForeignKey("hentai.id"))
    director_id: Mapped[int] = mapped_column(ForeignKey("director.id"))
    
    hentai: Mapped["Hentai"] = relationship("Hentai", back_populates="director_associations")
    director: Mapped["Director"] = relationship("Director", back_populates="hentais", lazy="joined")
    
class StudioHentai(Base):
    __tablename__ = "studio_hentai"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    hentai_id: Mapped[int] = mapped_column(ForeignKey("hentai.id"))
    studio_id: Mapped[int] = mapped_column(ForeignKey("studio.id"))
    
    hentai: Mapped["Hentai"] = relationship("Hentai", back_populates="studio_associations")
    studio: Mapped["Studio"] = relationship("Studio", back_populates="hentais", lazy="joined")

class VoiceoverHentai(Base):
    __tablename__ = "voiceover_hentai"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    hentai_id: Mapped[int] = mapped_column(ForeignKey("hentai.id"))
    voiceover_id: Mapped[int] = mapped_column(ForeignKey("voiceover.id"))
    
    hentai: Mapped["Hentai"] = relationship("Hentai", back_populates="voiceover_associations")
    voiceover: Mapped["Voiceover"] = relationship("Voiceover", back_populates="hentais", lazy="joined")
    
class SubtitlesHentai(Base):
    __tablename__ = "subtitles_hentai"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    hentai_id: Mapped[int] = mapped_column(ForeignKey("hentai.id"))
    subtitles_id: Mapped[int] = mapped_column(ForeignKey("subtitles.id"))
    
    hentai: Mapped["Hentai"] = relationship("Hentai", back_populates="subtitles_associations")
    subtitles: Mapped["Subtitles"] = relationship("Subtitles", back_populates="hentais", lazy="joined")
    
class GenresHentai(Base):
    __tablename__ = "genres_hentai"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    hentai_id: Mapped[int] = mapped_column(ForeignKey("hentai.id"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))  # Исправлено: genres_id → genre_id для единообразия
    
    hentai: Mapped["Hentai"] = relationship("Hentai", back_populates="genres_associations")
    genre: Mapped["Genres"] = relationship("Genres", back_populates="hentais", lazy="joined")

@dataclass
class Hentai(Base):
    __tablename__ = "hentai"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    poster: Mapped[str] = mapped_column(String(2048))
    url: Mapped[str] = mapped_column(String(2048))
    
    rating: Mapped[float] = mapped_column(Float(), nullable=True)
    premier: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    all_iframe: Mapped[List[str]] = mapped_column(JSON())

    director_associations: Mapped[List["DirectorHentai"]] = relationship(
        "DirectorHentai",
        back_populates="hentai",
        lazy="joined"
    )
    studio_associations: Mapped[List["StudioHentai"]] = relationship(
        "StudioHentai",
        back_populates="hentai",
        lazy="joined"
    )
    voiceover_associations: Mapped[List["VoiceoverHentai"]] = relationship(
        "VoiceoverHentai", 
        back_populates="hentai",
        lazy="joined"
    )
    subtitles_associations: Mapped[List["SubtitlesHentai"]] = relationship(
        "SubtitlesHentai", 
        back_populates="hentai",
        lazy="joined"
    )
    genres_associations: Mapped[List["GenresHentai"]] = relationship(
        "GenresHentai", 
        back_populates="hentai",
        lazy="joined"
    )
    
    @property
    def directors(self) -> List[Director]:
        return [assoc.director for assoc in self.director_associations]
    
    @property
    def studios(self) -> List[Studio]:
        return [assoc.studio for assoc in self.studio_associations]
    
    @property
    def voiceovers(self) -> List[Voiceover]:
        return [assoc.voiceover for assoc in self.voiceover_associations]
    
    @property
    def subtitles_list(self) -> List[Subtitles]:
        return [assoc.subtitles for assoc in self.subtitles_associations]
    
    @property
    def genres_list(self) -> List[Genres]:
        return [assoc.genre for assoc in self.genres_associations]