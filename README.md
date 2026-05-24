# 🎓 EduRank — Engineering College Selection Platform

> **Production-ready** Flask + PostgreSQL platform for exploring, comparing, and shortlisting engineering colleges in India.  
> Data sourced from NIRF 2024, AICTE, JoSAA, and AP/TS EAMCET counseling portals.

---

## 📁 Project Structure

```
engineering_college_platform/
│
├── run.py                         # Development server entry point
├── config.py                      # Dev / Prod / Test configurations
├── requirements.txt               # Python dependencies
├── Procfile                       # Render production start command
├── render.yaml                    # Render deployment config
├── .env.example                   # Environment variable template
│
├── app/
│   ├── __init__.py                # Flask app factory
│   ├── models/
│   │   └── __init__.py            # SQLAlchemy ORM models (all tables)
│   ├── blueprints/
│   │   ├── main/__init__.py       # Home, dashboard, favorites, compare
│   │   ├── auth/__init__.py       # Signup, login, logout
│   │   ├── colleges/__init__.py   # Search, filter, college detail
│   │   ├── admin/__init__.py      # Admin dashboard, users, CSV import
│   │   └── api/__init__.py        # REST API v1 (JSON endpoints)
│   ├── utils/
│   │   ├── forms.py               # WTForms (signup, login, search, upload)
│   │   └── helpers.py             # Jinja2 template filters
│   ├── static/
│   │   ├── css/main.css           # Full custom stylesheet
│   │   └── js/main.js             # Favorites, compare, toasts
│   └── templates/
│       ├── base.html              # Master layout (navbar, footer)
│       ├── main/                  # Home, dashboard, favorites, compare
│       ├── auth/                  # Login, signup
│       ├── colleges/              # Search, detail, card partial
│       ├── admin/                 # Dashboard, users, import
│       └── errors/                # 404, 500
│
├── scripts/
│   ├── seed_admin.py              # Seeds admin user + lookup tables
│   └── import_colleges.py        # CSV import engine (CLI + API)
│
├── data/
│   └── sample_csvs/
│       ├── nirf_2024_sample.csv   # 20 top NIRF colleges (real data)
│       ├── ap_ts_eamcet_sample.csv # AP/TS colleges
│       └── aicte_sample.csv       # AICTE-approved colleges
│
├── migrations/                    # Flask-Migrate auto-generated
└── tests/                         # (extend as needed)
```

---

## 🗃️ Database Schema

```
users           — Student/admin accounts (hashed passwords)
colleges        — Core college entity (name, rank, fees, placements…)
states          — Indian states lookup
cities          — Cities linked to states
branches        — Engineering disciplines (CSE, ECE, MECH…)
facilities      — Campus amenities (Hostel, Library, Sports…)
courses         — B.Tech/M.Tech programs offered per college
college_branch  — Many-to-many: colleges ↔ branches
college_facility— Many-to-many: colleges ↔ facilities
favorites       — User ↔ College wishlist
comparisons     — Stored comparison sessions
import_logs     — CSV import audit trail
```

---

## ⚙️ Local Setup (Step-by-Step)

### Prerequisites
- Python 3.10+
- PostgreSQL (local or Neon cloud)
- Git

### Step 1 — Clone and create virtual environment
```bash
git clone https://github.com/yourname/edurank.git
cd edurank
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure environment variables
```bash
cp .env.example .env
# Edit .env with your values:
nano .env
```

Required `.env` values:
```env
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/edurank_db
FLASK_ENV=development
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourStrongPassword123!
```

### Step 4 — Create the PostgreSQL database
```bash
# Option A: Local PostgreSQL
psql -U postgres -c "CREATE DATABASE edurank_db;"

# Option B: Use Neon PostgreSQL (see Neon Setup section below)
# Just paste the Neon connection string in DATABASE_URL
```

### Step 5 — Initialize database tables
```bash
flask db init          # Creates migrations/ folder (first time only)
flask db migrate -m "Initial schema"
flask db upgrade       # Creates all tables in PostgreSQL
```

Or just run the app once — it will auto-create tables via `db.create_all()`:
```bash
python run.py
```

### Step 6 — Seed admin user and lookup data
```bash
python scripts/seed_admin.py
```

This creates:
- Admin user (email/password from `.env`)
- 33 Indian states/UTs
- 25 engineering branches (CSE, ECE, MECH…)
- 18 campus facilities

### Step 7 — Import real college data
```bash
# Import NIRF 2024 sample (20 top colleges)
python scripts/import_colleges.py \
    --file data/sample_csvs/nirf_2024_sample.csv \
    --source NIRF

# Import AP/TS colleges
python scripts/import_colleges.py \
    --file data/sample_csvs/ap_ts_eamcet_sample.csv \
    --source AP_EAMCET

# Import AICTE data
python scripts/import_colleges.py \
    --file data/sample_csvs/aicte_sample.csv \
    --source AICTE
```

### Step 8 — Run the development server
```bash
python run.py
# Visit: http://localhost:5000
```

---

## 🌐 Neon PostgreSQL Setup

### Step 1 — Create Neon account
1. Go to [https://neon.tech](https://neon.tech) and sign up free
2. Click **New Project** → Name it `edurank`
3. Select **Region** closest to your users (e.g., AWS US East for India latency)

### Step 2 — Get connection string
1. In Neon dashboard → **Connection Details** tab
2. Copy the **Connection string** — it looks like:
   ```
   postgresql://user:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Paste this as `DATABASE_URL` in your `.env` file

### Step 3 — Verify connection
```bash
python3 -c "
from config import ProductionConfig
import psycopg2
conn = psycopg2.connect('YOUR_NEON_URL')
print('✅ Neon connection successful!')
conn.close()
"
```

### Important Notes for Neon:
- Always include `?sslmode=require` at the end of the URL
- Neon free tier: 512MB storage, 1 compute unit, auto-suspend after 5 min inactivity
- Connection pooling: use `?sslmode=require&connect_timeout=10`

---

## 🚀 Deploy to Render

### Step 1 — Push your code to GitHub
```bash
git init
git add .
git commit -m "Initial commit — EduRank"
git remote add origin https://github.com/yourname/edurank.git
git push -u origin main
```

### Step 2 — Create a new Render Web Service
1. Go to [https://render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub account and select the `edurank` repository
3. Configure:
   - **Name**: `edurank-college-platform`
   - **Environment**: `Python 3`
   - **Region**: Singapore (closest to India)
   - **Build Command**: `pip install -r requirements.txt && python scripts/seed_admin.py`
   - **Start Command**: `gunicorn run:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120`
   - **Plan**: Free (for testing) or Starter ($7/month for production)

### Step 3 — Set Environment Variables in Render
In Render dashboard → **Environment** tab, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (click "Generate" for a secure random value) |
| `DATABASE_URL` | Your Neon PostgreSQL connection string |
| `FLASK_ENV` | `production` |
| `ADMIN_EMAIL` | `admin@yourdomain.com` |
| `ADMIN_PASSWORD` | `YourSecurePass123!` |
| `WTF_CSRF_ENABLED` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |

### Step 4 — Deploy
Click **Create Web Service** — Render will:
1. Pull your code
2. Run `pip install -r requirements.txt`
3. Run `python scripts/seed_admin.py` (seeds admin + lookup tables)
4. Start gunicorn

### Step 5 — Import college data via Admin Panel
1. Visit `https://your-app.onrender.com/auth/login`
2. Login with your admin credentials
3. Go to **Admin** → **Import Data**
4. Upload `data/sample_csvs/nirf_2024_sample.csv` with source `NIRF`
5. Repeat for other CSV files

---

## 📊 Importing Real Data

### Getting Real NIRF Data
1. Visit [https://www.nirfindia.org/Rankings/2024/EngineeringRanking.html](https://www.nirfindia.org/Rankings/2024/EngineeringRanking.html)
2. Download the Excel/CSV from the page
3. Rename columns to match our format (see CSV Column Reference below)
4. Import via Admin Panel

### Getting AICTE Data
1. Visit [https://www.aicte-india.org/bureaus/ARIIA](https://www.aicte-india.org/bureaus/ARIIA)
2. Download the approved institutions list as Excel
3. Convert to CSV and map columns

### Getting JoSAA Data
1. Visit [https://josaa.nic.in](https://josaa.nic.in)
2. Download opening/closing ranks and seat matrix
3. Map to our `courses` table format for cutoff data

### AP EAMCET Data
1. Visit [https://sche.aptonline.in/EAMCET](https://sche.aptonline.in/EAMCET)
2. Download the college-wise seat allotment CSV

### CSV Column Reference (complete)

| Column | Required | Type | Example |
|--------|----------|------|---------|
| `name` | ✅ Yes | Text | IIT Bombay |
| `state` | ✅ Yes | Text | Maharashtra |
| `city` | No | Text | Mumbai |
| `short_name` | No | Text | IIT Bombay |
| `college_type` | No | Text | Government/Private/Deemed |
| `establishment_year` | No | Integer | 1958 |
| `aicte_id` | No | Text | 1-3760088584 |
| `nirf_rank` | No | Integer | 1 |
| `nirf_score` | No | Float | 89.72 |
| `nirf_year` | No | Integer | 2024 |
| `naac_grade` | No | Text | A++ |
| `annual_fees_min` | No | Integer (₹) | 250000 |
| `annual_fees_max` | No | Integer (₹) | 350000 |
| `placement_percentage` | No | Float (0–100) | 95.5 |
| `avg_package_lpa` | No | Float | 18.5 |
| `highest_package_lpa` | No | Float | 150.0 |
| `hostel_available` | No | Yes/No | Yes |
| `boys_hostel` | No | Yes/No | Yes |
| `girls_hostel` | No | Yes/No | Yes |
| `affiliated_university` | No | Text | Autonomous |
| `autonomous` | No | Yes/No | Yes |
| `official_website` | No | URL | https://iitb.ac.in |
| `email` | No | Email | info@iitb.ac.in |
| `phone` | No | Text | +91-22-2572-2545 |
| `address` | No | Text | Powai, Mumbai 400076 |
| `pincode` | No | Text | 400076 |
| `branches` | No | Comma-separated | CSE,ECE,MECH |
| `facilities` | No | Comma-separated | Library,Hostel (Boys) |
| `top_recruiters` | No | Comma-separated | Google,Microsoft |
| `description` | No | Text | Long description… |
| `total_seats` | No | Integer | 1000 |

---

## 🔌 REST API Reference

All endpoints return JSON. Authentication via session cookie.

```
GET  /api/v1/colleges              List/search colleges
GET  /api/v1/colleges/<id>         Full college detail
GET  /api/v1/states                All Indian states
GET  /api/v1/branches              All engineering branches
GET  /api/v1/favorites             Current user's favorites (auth required)
```

**Example:**
```bash
curl "https://your-app.onrender.com/api/v1/colleges?state=Karnataka&branch=Computer+Science+Engineering&nirf_max=50"
```

---

## 🔐 Security Features

- **Password Hashing**: Werkzeug PBKDF2-SHA256 (256-bit salted hash)
- **CSRF Protection**: Flask-WTF tokens on all POST forms
- **Session Security**: HTTPOnly + SameSite=Lax cookies; Secure flag in production
- **SQL Injection**: SQLAlchemy ORM parameterized queries (no raw SQL)
- **XSS Prevention**: Jinja2 auto-escaping on all template variables
- **Admin Protection**: `@admin_required` decorator on all admin routes
- **Safe Redirects**: Only relative URLs accepted for `next` redirect after login

---

## 🧪 Running Tests

```bash
# Set test environment
export FLASK_ENV=testing

# Run tests (extend tests/ folder)
python -m pytest tests/ -v
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, Flask 3.0 |
| ORM | SQLAlchemy 2.0 + Flask-Migrate |
| Database | PostgreSQL (Neon) |
| Auth | Flask-Login + Flask-Bcrypt |
| Forms | Flask-WTF + WTForms |
| Frontend | Bootstrap 5.3 + Custom CSS |
| Fonts | Syne + DM Sans (Google Fonts) |
| Charts | Chart.js 4.4 (admin) |
| CSV Processing | Pandas |
| Production Server | Gunicorn |
| Hosting | Render |
| DB Hosting | Neon PostgreSQL |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/compare-export`
3. Commit changes: `git commit -m "Add PDF export for comparison"`
4. Push: `git push origin feature/compare-export`
5. Open a Pull Request

---

## 📄 License

MIT License — free for educational and commercial use.

---

*Data sourced from publicly available NIRF 2024, AICTE, JoSAA datasets.*
