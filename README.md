Absolutely! Here's your complete `README.md` file content for **Fitrat ERP** — ready to copy and paste into your repo root.

---

````markdown
# 💼 Fitrat ERP

**Fitrat ERP** is a powerful, full-featured ERP system built for educational institutions and training centers.
It’s developed using **Django**, **Django REST Framework**, **Docker**, and a modern **Next.js frontend**. 
Fitrat is modular, scalable, and ready for production with payment integrations, Telegram bots, attendance systems, and more.

---

## 🌐 Project Repositories

- 🧠 **Backend**: [Fitrat ERP Backend](https://github.com/ShohjahonObruyevOybekovich/Fitrat-ERP)
- 🎨 **Frontend**: [Fitrat ERP Frontend](https://github.com/Sadriddin0124/fitrat_erp)

---

## ⚙️ Features

- ✅ Lead & Student Management
- ✅ Staff & Role System
- ✅ Task, Attendance & Finance Modules
- ✅ Payme & Click UZ Payment Integration
- ✅ Telegram Bot Support
- ✅ External APIs: Sayqal & TicTac Integration
- ✅ Dockerized Backend
- ✅ SSL-Ready NGINX Deployment
- ✅ Admin Panel Included

---

## 🧰 Backend Setup

### 1. Clone & Navigate

```bash
git clone https://github.com/ShohjahonObruyevOybekovich/Fitrat-ERP.git
cd Fitrat-ERP
````

### 2. Add `.env` File

Create `.env` in the project root and paste this:

```env
# SECURITY
SECRET_KEY='django-insecure-...'
ALLOWED_HOSTS=127.0.0.1,localhost:3000,api.ft.sector-soft.ru,ft.sector-soft.ru,...

# DATABASE
POSTGRES_DB="fitrat"
POSTGRES_USER="fitrat_user"
POSTGRES_PASSWORD="fitrat_db_pass01#"
POSTGRES_HOST="postgres"
POSTGRES_PORT=5432

DEBUG=True
DATABASE_URL=postgres://postgres:1@localhost:5432/fitrat

# PROJECT
COMPOSE_PROJECT_NAME=fitrat_ilm

# TELEGRAM BOT
WEBHOOK_SECRET=your_webhook_secret
BOT_TOKEN=your_bot_token

# PAYME
PAYME_ID="..."
PAYME_KEY="..."
PAYME_ACCOUNT_FIELD="id"
PAYME_ACCOUNT_MODEL="student.student.model.Student"
PAYME_ONE_TIME_PAYMENT=False

# CLICK UZ
CLICK_SERVICE_ID="..."
CLICK_MERCHANT_ID="..."
CLICK_SECRET_KEY="..."
CLICK_ACCOUNT_MODEL="clickuz.models.Order"
CLICK_AMOUNT_FIELD="amount"

# INTEGRATIONS
TT_URL="https://api.tictac.sector-soft.ru/restapi"
INTEGRATION_TOKEN="abcd1234"
SAYQAL_USERNAME=sectorsoft
SAYQAL_TOKEN=b2ddd7d417519...
```

### 3. Fix Docker Ports

Update exposed ports if necessary:

```bash
nano docker-compose.yaml
```

### 4. Start Backend

```bash
docker compose up -d --build
```

### 5. Enter Django Container

```bash
docker compose exec django sh
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌍 NGINX Setup

### Example Server Block

```nginx
server {
    server_name ft.sector-soft.ru;

    location / {
        proxy_pass http://localhost:8000;
        include proxy_params;
    }

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

### Enable HTTPS with Certbot

```bash
sudo certbot --nginx
```

---

## 🎨 Frontend Setup

### 1. Clone & Navigate

```bash
git clone https://github.com/Sadriddin0124/fitrat_erp.git
cd fitrat_erp
```

### 2. Configure `.env`

```env
NEXT_PUBLIC_API_URL=https://api.ft.sector-soft.ru
```

### 3. Fix `package.json` Port

```bash
nano package.json
# Change port if needed
```

### 4. Install & Build

```bash
pnpm install
pnpm build
```

### 5. Run with PM2

```bash
pm2 start npm --name fitrat_front -- start
pm2 save
pm2 restart all
```

---

## 📸 Screenshots

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/d69e7d17-81e7-45fa-9458-ba1905cd5a5c" />
<img width="1915" height="919" alt="image" src="https://github.com/user-attachments/assets/69820d51-39b7-483d-b606-c8d3bb6de1d4" />
<img width="1912" height="922" alt="image" src="https://github.com/user-attachments/assets/6c4770d6-7461-4cd5-b5ba-3d35fe0e896c" />
<img width="1917" height="918" alt="image" src="https://github.com/user-attachments/assets/c07481b9-9707-4b49-b85b-271e74df6016" />
<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/52c202c0-8cf7-4aeb-b9ed-d272021c2a20" />


---

## 🤝 Contribution

Got ideas? Issues? Fixes?
Fork the repo, create a branch, and make a PR. Contributions are more than welcome!

---

## 🔐 License

MIT — Use, modify, and deploy freely.

---

Developers:

- 🧠 **Backend**: [Shohjahon Obruyev](https://github.com/ShohjahonObruyevOybekovich)
- 🎨 **Frontend**: [Sadriddin Ravshanov](https://github.com/Sadriddin0124)

Built with ❤️ by SectorSoft and contributors.
