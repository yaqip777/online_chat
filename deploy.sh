#!/usr/bin/env bash
set -e

# ==============================================================
# ONLINE CHAT - PRODUCTION 1-CLICK DEPLOY SCRIPT
# ==============================================================

echo "🚀 Online Chat loyihasini yangilash va ishga tushirish..."

# .env faylini tekshirish
if [ ! -f .env ]; then
    echo "⚠️ .env fayli topilmadi. .env.example dan nusxalanmoqda..."
    cp .env.example .env
    echo "❗ Iltimos, .env faylidagi parollar va maxfiy kalitlarni to'ldiring!"
fi

# Uploads papkasini tekshirish
mkdir -p uploads

# Agar docker o'rnatilgan bo'lsa, Docker Compose orqali ishga tushirish
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "🐳 Docker Compose orqali konteynerlar qurilmoqda va ishga tushirilmoqda..."
    docker compose down --remove-orphans || true
    docker compose build --pull
    docker compose up -d

    echo "⏳ Konteynerlar holati tekshirilmoqda..."
    sleep 3
    docker compose ps

    echo "✅ Loyiha Docker orqali muvaffaqiyatli ishga tushirildi!"
    echo "📍 API Documentation: http://localhost:8000/docs"
    echo "📍 Healthcheck: http://localhost:8000/health"
    exit 0
fi

# Agar Docker bo'lmasa, mahalliy python muhiti orqali
echo "🐍 Mahalliy Python virtual muhitini sozlash..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Loyiha tayyor! Ishga tushirish uchun:"
echo "source .venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000"
