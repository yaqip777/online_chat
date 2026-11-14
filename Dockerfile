# ==============================================================
# ONLINE CHAT - PRODUCTION DOCKERFILE
# ==============================================================
FROM python:3.12-slim-bookworm

# Muhit o'zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Tizim paketlarini o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Xavfsizlik uchun non-root foydalanuvchi yaratish
RUN useradd -m -u 1000 appuser

# Bog'liqliklarni o'rnatish
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chirish
COPY . /app/

# Uploads papkasini yaratish va ruxsatlarni berish
RUN mkdir -p /app/uploads && \
    chown -R appuser:appuser /app

# Non-root foydalanuvchiga o'tish
USER appuser

# Port
EXPOSE 8000

# Server salomatligini tekshirish (Healthcheck)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production uvicorn serverni ishga tushirish
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
