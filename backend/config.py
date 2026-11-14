import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini yuklash (python-dotenv mavjud bo'lsa undan, bo'lmasa o'rnatilgan sodda parserdan foydalanamiz)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    env_file = BASE_DIR / ".env"
    if env_file.is_file():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Online Chat API")
    VERSION: str = os.getenv("VERSION", "1.0.0")

    # Ma'lumotlar bazasi
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/online_chat",
    )

    # Xavfsizlik kalitlari
    ACCESS_SECRET_KEY: str = os.getenv(
        "ACCESS_SECRET_KEY", "change-me-access-secret-key-32-bytes-long"
    )
    REFRESH_SECRET_KEY: str = os.getenv(
        "REFRESH_SECRET_KEY", "change-me-refresh-secret-key-32-bytes-long"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # CORS ruxsatnomalari
    _cors_raw = os.getenv("CORS_ORIGINS", '["*"]')
    try:
        CORS_ORIGINS: list[str] = json.loads(_cors_raw)
    except Exception:
        CORS_ORIGINS: list[str] = [
            item.strip() for item in _cors_raw.split(",") if item.strip()
        ] or ["*"]

    # Fayl yuklash sozlamalari
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", str(10 * 1024 * 1024)))
    MAX_VIDEO_SIZE: int = int(os.getenv("MAX_VIDEO_SIZE", str(50 * 1024 * 1024)))
    IMAGE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
    VIDEO_EXTENSIONS: list[str] = [".mp4", ".mov", ".mkv", ".webm"]

    def get_database_url(self) -> str:
        """PostgreSQL URLni asyncpg drayveri va SSL sozlamalari bilan moslashtirish."""
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # asyncpg drayveri 'sslmode=require' o'rniga 'ssl=require' parametrini tushunadi
        if "sslmode=" in url:
            url = url.replace("sslmode=", "ssl=")

        return url


settings = Settings()

# Uploads papkasini mavjudligini ta'minlash
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
