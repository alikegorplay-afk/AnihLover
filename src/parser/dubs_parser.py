import json
import re

from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from ..core.entites.schemas import M3U8Prewiev, M3U8Response
from .base import BaseParser

class DubingParser(BaseParser):
    # NOTE: Я не ебу как это работает но это работает!
    
    def extract(self, markup) -> Optional[M3U8Response]:
        soup = BeautifulSoup(markup, self.features)
        
        for script in soup.select("script"):
            script_text = script.get_text(strip=True)
            
            if "episodes:" not in script_text:
                continue
                
            try:
                # Извлекаем currentDub
                currentdub = self._extract_current_dub(script_text)
                if not currentdub:
                    continue
                
                # Извлекаем episodes данные
                episodes_data = self._extract_episodes(script_text)
                if not episodes_data:
                    continue
                
                return M3U8Response(**{
                    'dub_name': currentdub,
                    'all_m3u8': episodes_data
                })
                
            except (IndexError, json.JSONDecodeError, KeyError) as e:
                print(f"Ошибка при парсинге: {e}")
                continue
        
        return None
    
    def _extract_current_dub(self, script_text: str) -> Optional[str]:
        """Извлекает значение currentDub из скрипта"""
        try:
            # Ваш оригинальный метод
            return script_text.split("currentDub: '", 1)[1].split("',", 1)[0]
        except IndexError:
            # Альтернативный метод через регулярные выражения
            match = re.search(r"currentDub\s*:\s*'([^']+)'", script_text)
            return match.group(1) if match else None
    
    def _extract_episodes(self, script_text: str) -> Optional[List[M3U8Prewiev]]:
        """Извлекает массив episodes из скрипта"""
        try:
            # Ваш оригинальный метод
            episodes_str = "episodes: [{" + script_text.split("episodes: [{", 1)[1].split("}],", 1)[0] + "}]"
            
            # Используем регулярное выражение для более надежного извлечения
            match = re.search(r"episodes\s*:\s*(\[.*?\])", script_text, re.DOTALL)
            if match:
                episodes_str = match.group(1)
            
            # Заменяем JavaScript null на Python None для корректного парсинга JSON
            episodes_str = episodes_str.replace('null', 'null')
            
            iframes = []
            for data in json.loads(episodes_str):
                if data.get("url") is None:
                    continue
                iframes.append(M3U8Prewiev(**data))
            return iframes
            
        except (IndexError, json.JSONDecodeError):
            return None