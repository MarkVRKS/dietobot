import os
from pathlib import Path

BOT_TOKEN = os.getenv("BOT_TOKEN", "8770496712:AAHYy9EPF-VC-4KWDOiC7102TgKhVcE9hq0")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1195803601"))

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "data" / "bot.db"
