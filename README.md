# 💬 Online Chat Backend API

FastAPI, SQLAlchemy 2.0 (Asyncpg), PostgreSQL va WebSockets asosida yaratilgan zamonaviy ijtimoiy tarmoq va real-vaqtli xabarlashuv tizimi.

---

## ✨ Imkoniyatlar
- **Foydalanuvchilar va Autentifikatsiya**:
  - JWT Access va Refresh tokenlar orqali xavfsiz tizim
  - Gmail orqali ro'yxatdan o'tish va validatsiya
  - Profil rasmini yuklash va yangilash
  - Xavfsiz parollash (bcrypt)
- **Ijtimoiy tarmoq (Posts)**:
  - Postlar yaratish (matn, rasm, video)
  - Cursor-based pagination (katta hajmdagi ma'lumotlarda yuqori tezlik)
  - Layklar tizimi va postlarni o'chirish
- **Hikoyalar (Stories)**:
  - 24 soatlik avtomatik eskiruvchi hikoyalar (rasm, video)
  - Foydalanuvchilar bo'yicha faol hikoyalarni filtrlash
- **Obunalar (Follows)**:
  - Foydalanuvchilarga obuna bo'lish / obunani bekor qilish
  - Obunachilar va kuzatuvchilar ro'yxati (paginatsiya bilan)
- **Chat va Real-vaqtli Xabarlar**:
  - 1-ga-1 shaxsiy suhbatlar (matn, rasm, video fayllar)
  - WebSockets orqali real vaqtda xabarlarni yetkazish
- **Video Qo'ng'iroq (WebRTC Signalling)**:
  - WebSockets orqali video qo'ng'iroq signallari (offer, answer, ice-candidate, end)

---

## 🛠 Texnologiyalar
- **Til**: Python 3.12+
- **Asosiy Framework**: FastAPI
- **Ma'lumotlar bazasi**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (AsyncIO + asyncpg)
- **Validatsiya**: Pydantic v2
- **Konteynerlashtirish**: Docker & Docker Compose
- **Web Server**: Uvicorn & Nginx

---

## 🚀 Loyihani Ishga Tushirish

### 1. Docker orqali (Eng oson usul):
```bash
# 1. Muhit faylini yaratish
cp .env.example .env

# 2. Ishga tushirish
./deploy.sh
```
yoki:
```bash
docker compose up -d --build
```

### 2. Mahalliy Python muhitida:
```bash
# Virtual muhit yaratish
python3 -m venv .venv
source .venv/bin/activate

# Paketlarni o'rnatish
pip install -r requirements.txt

# .env faylini to'ldirish
cp .env.example .env

# Serverni ishga tushirish
uvicorn backend.main:app --reload --port 8000
```

---

## 📚 API Hujjatlari (Swagger UI)
Server ishga tushgandan so'ng:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📖 Serverga Joylash (Deployment)
Batafsil serverga joylash bo'yicha yo'riqnoma uchun [DEPLOYMENT.md](file:///home/amirxon/Desktop/online_chat/DEPLOYMENT.md) fayliga qarang.
