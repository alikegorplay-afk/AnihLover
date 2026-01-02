import asyncio
import re
import os

from pprint import pp

import aiohttp

from src.manager.anihidew import Anihidew
from src.manager.requesteng import RequestEngine
from src.manager.urlextractor import URLExtractor
from src.core import config

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
    async with aiohttp.ClientSession(**config.proxy) as session:
        engine = RequestEngine(session)
        
        url_api = URLExtractor(engine)
        hentai_api = Anihidew(engine)
        
        for hentai in await url_api.extract_top_rating():
            print(hentai.title)
            print(hentai.url)
            print(hentai.poster)
            print(hentai.rating)
            full_hentai = await hentai_api.get_hentai(hentai.url.encoded_string())
            if not full_hentai:
                continue
            
            pp(full_hentai.model_dump())
            print("#" * 50)
        

        

            
    
        
        
if __name__ == "__main__":
    asyncio.run(main())