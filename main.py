import asyncio
import re
import os

from urllib.parse import urljoin
from pathlib import Path

import aiohttp

from bs4 import BeautifulSoup

from src.manager.anihidew import Anihidew


def sanitize_filename(filename):
    if os.name == 'nt':
        invalid_chars = r'[<>:"|?*\\/]'
    else:
        invalid_chars = r'[/]'
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = re.sub(invalid_chars, '_', filename)
    filename = filename.strip()
    filename = re.sub(r'\s+', ' ', filename)
    
    return filename

async def main():
    async with aiohttp.ClientSession(

    ) as session:
        tasks = []
        api = Anihidew(session)
        
        soup = BeautifulSoup(await api.http.request("https://anihidew.org/hentai_top100_rating.html", 'text'), 'html.parser')
        
        for url in soup.select("a.poster.d-flex"):
        
            data = await api.get_hentai(url.get('href'))
            
            for i in data.all_iframe:
                iframe_data = await api.get_ifrmae(i.encoded_string())
                for m3u8 in [m3u8 for m3u8 in iframe_data.all_m3u8]:
                    m3u8_data = await api.get_m3u8(m3u8.url.encoded_string())
                    
                    
                    url = [urljoin(m3u8.url.encoded_string(), x) for x in m3u8_data.split("\n") if x and not x.startswith("#")]

                    directory = Path("data") / Path(iframe_data.dub_name + "-" + sanitize_filename(data.title))
                    directory.mkdir(parents=True, exist_ok=True)
                    
                    tasks.append(api.download_hentai(url[-1], directory / (m3u8.title + ".mp4")))
                    
            await asyncio.gather(*tasks)
        
        
if __name__ == "__main__":
    asyncio.run(main())