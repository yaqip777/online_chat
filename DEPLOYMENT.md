# 🚀 Serverga Joylash Bo'yicha To'liq Qo'llanma (Production Deployment Guide)

Ushbu qo'llanmada **Online Chat API** loyihasini Linux (Ubuntu / Debian) serverga joylashning 2 xil eng qulay usuli keltirilgan:
1. **Docker Compose orqali (Tavsiya etiladi - eng oson va xavfsiz)**
2. **Ubuntu VPS da to'g'ridan-to'g'ri (Systemd + Nginx + PostgreSQL)**

---

## 1-USUL: Docker Compose Orqali Joylash (Tavsiya etiladi)

Bu usulda PostgreSQL va FastAPI avtomatik tarzda konteynerlarda, bir-biriga bog'langan holda ishlaydi.

### 1-qadam: Serverga Docker va Docker Compose o'rnatish
Serveringizga kiring (SSH) va quyidagi buyruqlarni bajaring:

```bash
# Server paketlarini yangilash
sudo apt update && sudo apt upgrade -y

# Kerakli utilitalarni o'rnatish
sudo apt install -y curl git ufw

# Dockerni rasmiy skript orqali o'rnatish
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Joriy foydalanuvchiga docker huquqini berish
sudo usermod -aG docker $USER
newgrp docker
```

### 2-qadam: Loyihani serverga yuklab olish
```bash
git clone <LOYIHA_GIT_URLI> /var/www/online_chat
cd /var/www/online_chat
```

### 3-qadam: Muhit o'zgaruvchilarini (.env) sozlash
```bash
cp .env.example .env
nano .env
```

`.env` faylida quyidagi maxfiy kalitlarni o'zingizning yangi kalitlaringiz bilan almashtiring:
```bash
# Yangi 32 baytli maxfiy kalit yaratish uchun terminalda:
openssl rand -hex 32
```
Hosill bo'lgan kalitlarni `ACCESS_SECRET_KEY` va `REFRESH_SECRET_KEY` qatorlariga yozing.

### 4-qadam: Loyihani ishga tushirish
Shunchaki `deploy.sh` skriptini bajaring:
```bash
./deploy.sh
```
Yoki qo'lda:
```bash
docker compose up -d --build
```

### 5-qadam: Holatni tekshirish
```bash
docker compose ps
docker compose logs -f web
```
Server ishlayotganini tekshirish uchun:
```bash
curl http://localhost:8000/health
```

---

## 2-USUL: Ubuntu VPS da Nginx + Systemd Orqali Joylash

### 1-qadam: PostgreSQL o'rnatish va sozlash
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib python3-venv python3-pip nginx

# PostgreSQL ga kirish va baza yaratish
sudo -u postgres psql
```

PostgreSQL terminalida:
```sql
CREATE DATABASE online_chat;
CREATE USER online_chat_user WITH ENCRYPTED PASSWORD 'kuchli_parol_kiriting';
GRANT ALL PRIVILEGES ON DATABASE online_chat TO online_chat_user;
ALTER DATABASE online_chat OWNER TO online_chat_user;
\q
```

### 2-qadam: Loyihani sozlash
```bash
sudo mkdir -p /var/www/online_chat
sudo chown -R $USER:$USER /var/www/online_chat
cd /var/www/online_chat

# Virtual muhit yaratish
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# .env sozlash
cp .env.example .env
nano .env
```
`.env` fayliga bazangiz manzilini yozing:
```env
DATABASE_URL=postgresql+asyncpg://online_chat_user:kuchli_parol_kiriting@localhost:5432/online_chat
ACCESS_SECRET_KEY=yangi_maxfiy_kalit
REFRESH_SECRET_KEY=yangi_maxfiy_kalit
```

### 3-qadam: Systemd servis sozlash
```bash
sudo cp online_chat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable online_chat
sudo systemctl start online_chat
sudo systemctl status online_chat
```

### 4-qadam: Nginx va SSL (HTTPS) sozlash
```bash
sudo cp nginx/online_chat.conf /etc/nginx/sites-available/online_chat
sudo ln -s /etc/nginx/sites-available/online_chat /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx konfiguratsiyasini tekshirish
sudo nginx -t

# Nginx ni qayta yuklash
sudo systemctl reload nginx
```

Domen nomingiz bo'lsa, bepul Let's Encrypt SSL sertifikatini o'rnating:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d sizningdomeningiz.uz
```

---

## Muhim Havfsizlik va Xizmat Tavsiyalari:
1. **Firewall (UFW)**:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
2. **Fayllar zaxirasi (Backups)**:
   - Muntazam ravishda `/var/www/online_chat/uploads` papkasini va PostgreSQL ma'lumotlar bazasini `pg_dump` orqali zaxiralab turing.
