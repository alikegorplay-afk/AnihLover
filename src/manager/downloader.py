import subprocess
import asyncio

from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from urllib.parse import urljoin
from pathlib import Path

import aiofiles

from loguru import logger

from .requesteng import RequestEngine

class DownloadManager:
    """Менеджер для загрузок видео"""
    
    def __init__(self, http: RequestEngine, max_workers: int = 5):
        """Инцилизация DownloadManager

        Args:
            http (RequestEngine): Логика запросов
            max_workers (int, optional): Максимальное количество сборщиков видео. Базовое значение 5.
        """
        self.http = http
        self.executer = ThreadPoolExecutor(max_workers = max_workers)
        
    async def download_by_m3u8(self, url: str, path: str = "video.mp4"):
        """Скачивает видео по ссылке на m3u8-плейлист.

        Args:
            url (str): Ссылка на .m3u8 файл.
            path (str): Путь для сохранения итогового видео. По умолчанию — "video.mp4".
        """
        # Получаем содержимое m3u8
        m3u8_text = await self.http.request(url, 'text', self.http._m3u8_headers())
        if not m3u8_text:
            logger.error("Не удалось получить M3U8-плейлист")
            return

        # Извлекаем URL'ы чанков
        urls = self._extract_urls(url, m3u8_text)

        # Временная директория для .ts файлов
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Скачиваем все чанки параллельно
            download_tasks = [
                self._download_chunk(u, tmpdir, index)
                for index, u in enumerate(urls, start=1)
            ]
            await asyncio.gather(*download_tasks)

            # Создаём input.txt для ffmpeg в порядке номеров чанков
            input_file = tmpdir / "input.txt"
            async with aiofiles.open(input_file, 'w') as f:
                for ts_file in sorted(tmpdir.glob("*.ts"), key=lambda p: int(p.name.split('-')[0])):
                    await f.write(f"file '{ts_file}'\n")

            # Собираем видео через ffmpeg в отдельном потоке
            await asyncio.get_event_loop().run_in_executor(
                self.executer,
                lambda: self._build_video(tmpdir, path)
            )

                        
    async def _download_chunk(self, url: str, path: Path | str, index: int):
        """Скачивает чанк .ts файла."""
        path = Path(path)
        filename = f"{index}-{sha256(url.encode()).hexdigest()[:64]}.ts"
        filepath = path / filename

        response = await self.http.request(url, 'bytes', self.http._m3u8_headers())
        if response is None:
            logger.warning(f"Не удалось получить фрагмент (url={url})")
            return

        async with aiofiles.open(filepath, 'wb') as file:
            await file.write(response)

    
    def _extract_urls(self, base_url: str, response: str) -> list[str]:
        """Извлекает ссылки из m3u8"""
        urls = []
        for line in response.split("\n"):
            if not line.strip():
                continue
            if line.startswith("#"):
                continue
            
            urls.append(urljoin(base_url, line))
        return urls
    
    def _build_video(self, tmpdir: Path, path: str):
        """Собирает видео"""
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                f'{tmpdir / "input.txt"}',
                "-c",
                "copy",
                str(path)
            ]
        )