# Accessory IMS — Django Setup Guide

## Local Setup (First Time)

### 1. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and update `DATABASE_URL` with your PostgreSQL credentials:
```
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/accessory_ims
```

### 4. Create the database
In psql or pgAdmin, create a database named `accessory_ims`:
```sql
CREATE DATABASE accessory_ims;
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start the server
```bash
python manage.py runserver
```

### 7. Open in browser
Visit `http://localhost:8000` — you'll be redirected to the setup page.
Complete the one-time store setup (store name, categories, admin account).

---

## Daily Use

```bash
source venv/bin/activate
python manage.py runserver
```
Open `http://localhost:8000`

---

## Deploy to Render

1. Push code to a GitHub repository
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your GitHub repo — Render detects `render.yaml` automatically
4. Add environment variables in the Render dashboard:
   - `SECRET_KEY` — generate a random string
   - `DEBUG` — set to `False`
5. Deploy. Render provisions PostgreSQL and persistent disk automatically.

---

## Roles

| Role | Can Do |
|------|--------|
| Admin | Full access: products, sales, reports, PDF export, staff management |
| Attendant | Sell products, do stock counts |

---

## Troubleshooting

**"relation does not exist" error** → Run `python manage.py migrate`

**Images not showing** → Make sure `MEDIA_ROOT` folder exists and is writable

**Can't log in after setup** → Check your username exactly as entered during setup
