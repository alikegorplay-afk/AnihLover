import subprocess
import asyncio

from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from urllib.parse import urljoin
from pathlib import Path

import aiofiles

from loguru import logger

from .requesteng import RequestEngine

class DownloadManager:
    def __init__(self, http: RequestEngine, max_workers: int = 5):
        self.http = http
        self.executer = ThreadPoolExecutor(max_workers = max_workers)
        
    async def download(self, url: str, path: str = "video.mp4"):
        response = await self.http.request(url, 'text', self.http._m3u8_headers())
        
        if response is None:
            logger.error('Не удалось скачать видео так-как не удалось получить M3U8')
            return
        
        urls = self._extract_urls(url, response)
            
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            tasks = [asyncio.create_task(self._download_chunk(url, tmpdir, indx)) for indx, url in enumerate(urls, 1)]
            await asyncio.gather(*tasks)
            
            async with aiofiles.open(tmpdir / "input.txt", 'w') as file:
                for ts in sorted(tmpdir.glob("*.ts"), key = lambda x: int(x.name.split('.')[0])):
                    await file.write(f"file '{str(ts)}'" + "\n")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executer,
                func = lambda: self._buidl_video(tmpdir, path)
            )
                        
    async def _download_chunk(self, url: str, path: Path | str, index: int):
        path = Path(path)
        async with aiofiles.open(path / (str(index) + ".ts"), 'wb') as file:
            response = await self.http.request(url, 'bytes', self.http._m3u8_headers())
            if response is None:
                logger.warning(f"Не удалось получит фрагмент (url={url})")
                return
            
            await file.write(response)
    
    def _extract_urls(self, base_url: str, response: str) -> list[str]:
        urls = []
        for line in response.split("\n"):
            if not line.strip():
                continue
            if line.startswith("#"):
                continue
            
            urls.append(urljoin(base_url, line))
        return urls
    
    def _buidl_video(self, tmpdir: Path, path: str):
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