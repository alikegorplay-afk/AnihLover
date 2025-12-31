import os

os.environ['DB_URL'] = "sqlite+aiosqlite:///data.db"
print(os.environ)

from src.core import config

print(config.BD_URL)