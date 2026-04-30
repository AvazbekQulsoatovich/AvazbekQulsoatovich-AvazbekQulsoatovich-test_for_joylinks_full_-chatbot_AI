# Joylinks IT - Education Management System (Production Ready)

Ushbu platforma o'quv markazlari va IT maktablar uchun mo'ljallangan bo'lib, 500 dan ortiq bir vaqtning o'zidagi foydalanuvchilarni (concurrent users) muammosiz qo'llab-quvvatlaydi. Tizim yuqori xavfsizlik va performans standartlari asosida qurilgan.

---

## 🚀 Deployment (Serverga o'rnatish)

Tizimni serverga o'rnatish uchun **Docker** va **Docker Compose** tavsiya etiladi. Bu barcha texnologiyalarni (Postgres, Nginx, Flask) bir vaqtda va xatosiz ishga tushirishni ta'minlaydi.

### 1. Talablar (Prerequisites)
Serverda quyidagilar o'rnatilgan bo'lishi shart:
- Docker
- Docker Compose
- Git

### 2. O'rnatish qadamlari
1. Loyhani serverga clone qiling:
   ```bash
   git clone <REPO_URL>
   cd test_for_joylinks_full-main
   ```

2. `.env` faylini yarating va sozlang:
   ```bash
   cp .env.example .env  # Agar .env.example bo'lsa, aks holda yangi yarating
   ```

3. Tizimni ishga tushiring:
   ```bash
   docker-compose up --build -d
   ```

Tizim ishga tushgach:
- **Web App**: `http://server-ip`
- **Admin Panel**: `http://server-ip/login`

---

## 🔧 Konfiguratsiya (.env)

Tizim ishlashi uchun `.env` faylida quyidagi o'zgaruvchilar bo'lishi shart:

| O'zgaruvchi | Tavsif | Misol / Standart |
| :--- | :--- | :--- |
| `FLASK_ENV` | Ishlash muhiti | `production` |
| `SECRET_KEY` | Xavfsizlik kaliti | `ixtiyoriy_murakkab_kod` |
| `DATABASE_URL` | Ma'lumotlar bazasi | `postgresql://user:pass@host:5432/db` |
| `GROQ_API_KEY` | AI Chatbot uchun | `gsk_...` (https://console.groq.com/) |
| `GEMINI_API_KEY` | AI Analytics uchun | `AIza...` (https://aistudio.google.com/) |
| `DEFAULT_ADMIN_PASS` | Admin paroli | `admin123` |

---

## 🔑 Admin Kirish (Default)

Tizim birinchi marta ishga tushganda avtomatik ravishda quyidagi superadmin akkauntini yaratadi:
- **Username**: `admin`
- **Password**: `secure_admin_password_2024` (Agarda `.env` da o'zgartirilmagan bo'lsa)
- **Role**: Super Admin

---

## 🏗️ Arxitektura (Tech Stack)

- **Backend**: Python Flask (Gunicorn server bilan)
- **Frontend**: Shaffof va zamonaviy Gray UI (Vanilla JS & CSS)
- **Database**: PostgreSQL (Production-grade ma'lumotlar saqlash)
- **Proxy**: Nginx (Static fayllarni tezkor uzatish va xavfsizlik uchun)
- **Container**: Docker & Docker Compose

---

## 🛠️ Texnik Xizmat Ko'rsatish (Maintenance)

- **Loglarni ko'rish**:
  ```bash
  docker-compose logs -f web
  ```
- **Tizimni to'xtatish**:
  ```bash
  docker-compose down
  ```
- **Bazani qayta initsializatsiya qilish**:
  Docker konteyneri ishga tushganda `init_prod_db.py` avtomatik ishlaydi va schema mavjud bo'lmasa uni yaratadi.

---

## 🛡️ Xavfsizlik (Security Features)
- CSRF Protection barcha formalarda mavjud.
- Rate Limiting (Brute-force hujumlaridan himoya).
- Session isolation (Filiallar o'rtasida ma'lumotlar daxlsizligi).
- Secure Cookies (HTTPS yoqilganda).

**Dasturchi**: Antigravity AI
**Sana**: 2026-yil Aprel

