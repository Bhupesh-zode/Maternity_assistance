# Maternity Assistance — Childbirth Prediction

A Django web application that helps expectant users understand recommended childbirth modes (e.g. vaginal vs cesarean) using an XGBoost ML model. The platform also includes a pregnancy assistant, direct admin support chat, appointment booking, prediction history, and in-app notifications.

**Repository:** [github.com/Bhupesh-zode/Maternity_assistance](https://github.com/Bhupesh-zode/Maternity_assistance)

**Stack:** Django 4.1.7 · MySQL 8 · scikit-learn · XGBoost · pandas · Google Gemini (`google-generativeai`)

---

## Table of contents

1. [What this application does](#1-what-this-application-does)
2. [How the three portals work](#2-how-the-three-portals-work)
3. [Prerequisites](#3-prerequisites)
4. [First-time setup](#4-first-time-setup)
5. [Run the project daily](#5-run-the-project-daily)
6. [Log in and test](#6-log-in-and-test)
   - [Seed demo data (college presentation)](#seed-demo-data-college-presentation)
7. [User guide — step by step](#7-user-guide--step-by-step)
8. [Admin guide — step by step](#8-admin-guide--step-by-step)
9. [Feature reference](#9-feature-reference)
10. [URL map](#10-url-map)
11. [Database tables](#11-database-tables)
12. [Project structure](#12-project-structure)
13. [Configuration](#13-configuration)
14. [Troubleshooting](#14-troubleshooting)
15. [Security (development only)](#15-security-development-only)
16. [GitHub collaboration](#16-github-collaboration)

---

## 1. What this application does

| Goal | How the app helps |
|------|-------------------|
| **Predict childbirth mode** | User fills a clinical form → XGBoost model returns a recommendation |
| **Pregnancy guidance** | AI assistant with trimester tips, red-flag checks, and optional Gemini replies |
| **Talk to admin** | Private user–admin messaging with text and file attachments |
| **Book consultations** | Users request appointment slots; admin confirms or reschedules |
| **Track predictions** | Every predict run is saved; users and admins can review history |
| **Stay informed** | Unread badges and an alerts page for messages, appointments, and predictions |

---

## 2. How the three portals work

```
┌─────────────────────────────────────────────────────────────────┐
│  PUBLIC SITE          │  USER PORTAL         │  ADMIN PORTAL      │
│  (no login)           │  (session: sno)      │  (admin session)   │
├───────────────────────┼──────────────────────┼────────────────────┤
│  Home, About, Contact │  Dashboard           │  Dashboard         │
│  Register             │  Predict + History   │  Manage users      │
│  User / Admin login   │  Profile             │  Dataset + ML runs │
│                       │  Assistant (AI chat) │  Algorithm compare │
│                       │  Messages + files    │  User messages     │
│                       │  Appointments        │  Appointments      │
│                       │  Alerts              │  Prediction history│
└───────────────────────┴──────────────────────┴────────────────────┘
```

**Typical user flow:** Register → Admin approves → Login → Predict → Use assistant / message admin / book appointment.

**Typical admin flow:** Login → Approve pending users → Reply to messages → Manage appointments → Review predictions and datasets.

---

## 3. Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python 3.10+** | Developed with 3.13 |
| **MySQL Server 8.0** | Windows service name: `MySQL80` |
| **Git** | For clone and collaboration |
| **Optional** | [Google AI Studio](https://aistudio.google.com/apikey) API key for Gemini assistant |

On Windows, if `mysqlclient` fails to build, pre-built wheels usually work on Python 3.13. Visual C++ build tools may be needed otherwise.

---

## 4. First-time setup

Follow these steps in order. Do not skip `.env` or migrations.

### Step 1 — Clone and create a virtual environment

```powershell
git clone https://github.com/Bhupesh-zode/Maternity_assistance.git
cd Maternity_assistance

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
```

**Recommended install** (Python 3.10–3.13):

```powershell
pip install Django==4.1.7 pandas scikit-learn xgboost Pillow mysqlclient google-generativeai
```

> Use **`.venv`** only. Ignore old folders like `childenv3.11.1` or `env_testing3` if copied from another machine.

Optional: `pip install -r requirements.txt` — may fail on Python 3.13 (e.g. `PyYAML==6.0`).

### Step 2 — Start MySQL

Open **PowerShell as Administrator**:

```powershell
net start MySQL80
```

### Step 3 — Import the database

Adjust the path to your project folder:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pYOUR_PASSWORD -e "source C:/path/to/Maternity_assistance/childbirth.sql"
```

Verify:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pYOUR_PASSWORD -e "USE childbirth; SHOW TABLES;"
```

### Step 4 — Create `.env`

```powershell
copy .env.example .env
notepad .env
```

Example (do **not** commit this file):

```env
MYSQL_PASSWORD=your_mysql_root_password
DJANGO_SECRET_KEY=change-me-to-a-random-secret-key

# Optional — pregnancy assistant
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Step 5 — Run Django migrations

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py check
python manage.py check_ml_pickles
```

`migrate` creates all app tables (users, chat, support messages, predictions, appointments, notifications). `check_ml_pickles` verifies ML model files load correctly.

### Step 6 — Start the server

```powershell
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

> Always activate `.venv` before `runserver`. Using system Python without dependencies causes errors such as `No module named 'pandas'`.

> After pulling new code or editing `urls.py` / `settings.py`, restart the server (Ctrl+C, then `runserver` again).

---

## 5. Run the project daily

```powershell
cd path\to\Maternity_assistance
.\.venv\Scripts\Activate.ps1

# If MySQL stopped (Admin PowerShell):
# net start MySQL80

python manage.py runserver
```

---

## 6. Log in and test

### Admin

| Field | Value |
|-------|--------|
| URL | http://127.0.0.1:8000/adminlogin |
| Username | `admin` |
| Password | `admin` |

Credentials are hardcoded in `mainapp/views.py`. Change before any public deployment.

### Sample users (from `childbirth.sql`)

| Email | Password | Status |
|-------|----------|--------|
| `deepika@gmail.com` | `Dee258369` | accepted |
| `admin@gmail.com` | `1234` | accepted |
| `marnus@gmail.com` | `Ma12346` | restricted |

Login URL: http://127.0.0.1:8000/userlogin

New users register at `/register` with status **pending** until an admin approves them.

### Demo account (college presentation)

Use this account to walk through a fully populated user dashboard during demos:

| Field | Value |
|-------|--------|
| URL | http://127.0.0.1:8000/userlogin |
| Email | `bhupeshzode9@gmail.com` |
| Password | Your registered password for this account |
| Status | `accepted` (set automatically by the seed command) |

After seeding (below), this account includes prediction history, appointments, AI chat, support messages, and notifications so charts and badges look realistic.

### Seed demo data (college presentation)

A management command fills fake but realistic data for the demo account — predictions spread across the last 6 months (for dashboard charts), mixed appointment statuses, assistant chat, admin support thread, and alerts.

**Run once before a presentation** (with `.venv` activated):

```powershell
python manage.py seed_demo_user --email bhupeshzode9@gmail.com
```

**What gets created**

| Data | Count / detail |
|------|----------------|
| Prediction history | 8 runs (Vaginal birth & Cesarean section) over 6 months |
| Latest prediction | Synced to `user_predictions` for dashboard pill |
| Appointments | 4 — pending, confirmed, completed, rescheduled |
| AI assistant chat | 6 messages (trimester tips + how to use Predict) |
| Admin support | 4 messages with 1 unread admin reply |
| Notifications | 4 alerts with 2 unread |

**Re-run anytime** — the command clears existing demo data for that user first, then re-seeds from scratch.

**Seed a different user** (must already exist in the database):

```powershell
python manage.py seed_demo_user --email other@example.com
```

If the account is not `accepted`, the command sets status to `accepted` so login works.

**Demo checklist**

1. Run `seed_demo_user` (see above).
2. Log in as `bhupeshzode9@gmail.com`.
3. Open **Dashboard** — stats and all 3 activity charts should show data.
4. Open **Prediction History**, **Appointments**, **Messages**, and **Alerts** — each section should have content and unread badges where expected.

---

## 7. User guide — step by step

After logging in, the navbar gives access to all user features.

### 7.1 Dashboard

- URL: `/user-dashboard`
- Welcome panel with your name and latest prediction summary.
- Stat cards: total predictions, appointments, and unread messages.
- **Your activity** — three Chart.js charts from your real data:
  - Predictions over the last 6 months (line chart)
  - Appointments by status (doughnut chart)
  - Prediction outcomes (horizontal bar chart)
- Quick-action cards: Predict, Assistant, Messages, Appointments, and History.
- For a populated demo, run `python manage.py seed_demo_user` (see [Seed demo data](#seed-demo-data-college-presentation)).

### 7.2 Childbirth prediction

1. Go to **Predict** (`/user-predict`).
2. Fill in the clinical form and submit.
3. View the result page.
4. Latest result is saved to `user_predictions` and appended to **History**.

### 7.3 Prediction history

- URL: `/user-prediction-history`
- Lists every predict run with date, result, and key fields.
- Click **Details** on any row for the full form snapshot.

### 7.4 Pregnancy assistant (AI chat)

- URL: `/user-chat`
- General pregnancy tips, quick topics, red-flag checks.
- Optional Gemini AI if `GEMINI_API_KEY` is set in `.env`.
- Uses your **latest saved prediction** when you ask about predict results.
- **Not** the same as admin messaging — this is automated guidance only.

### 7.5 Message admin (private support)

- URL: `/user-messages`
- Private thread between you and admin only.
- Send text and/or attach files (images, PDF, DOC — max 10 MB).
- Unread admin replies show a badge on **Messages** in the navbar.

### 7.6 Book an appointment

1. Go to **Appointments** (`/user-appointments`).
2. Choose a future date and time slot (9 AM–4 PM).
3. Add optional notes and submit.
4. Track status: Pending → Confirmed / Rescheduled / Completed / Cancelled.
5. Cancel a request while it is still **Pending**.

### 7.7 Alerts and notifications

- URL: `/user-notifications`
- Badge on **Alerts** when you have unread items.
- Notifications are created when:
  - Admin replies in chat
  - A prediction is saved
  - An appointment status changes

---

## 8. Admin guide — step by step

Use the sidebar on any admin page. Badges highlight unread messages and pending appointments.

### 8.1 Approve new users

1. **Manage Users → Pending Users** (`/admin-pending-users`)
2. Approve or reject registrations.

### 8.2 Reply to user messages

1. Open **Messages** (`/admin-messages`) — inbox lists all user conversations.
2. Click **Open chat** on a user.
3. Reply with text and/or attach files (same rules as user side).
4. Unread count badge updates when users send new messages.

### 8.3 Manage appointments

1. Open **Appointments** (`/admin-appointments`).
2. For each request you can:
   - **Confirm** — accepts the user’s preferred slot
   - **Reschedule** — set a new date/time and optional note
   - **Cancel** — cancel with optional note to user
   - **Mark completed** — after a confirmed visit
3. User receives an in-app notification for each update.

### 8.4 View prediction history

- **Predictions** (`/admin-prediction-history`) — all users’ predict runs in one table.

### 8.5 Dataset and algorithms (existing)

- Upload / view dataset
- Run and compare ML algorithms (logistic regression, gradient boost, XGBoost, etc.)

---

## 9. Feature reference

### Public

| Feature | Description |
|---------|-------------|
| Home, About, Contact | Marketing and information pages |
| Register | New user signup (pending until admin approval) |
| User / Admin login | Entry points for each portal |

### User portal

| Feature | URL | Description |
|---------|-----|-------------|
| Dashboard | `/user-dashboard` | Main hub after login |
| Profile | `/user-profile` | Edit name, contact, photo |
| Predict | `/user-predict` | ML childbirth mode prediction |
| History | `/user-prediction-history` | All past predict runs |
| Appointments | `/user-appointments` | Book and track consultations |
| Assistant | `/user-chat` | AI pregnancy chat (Gemini optional) |
| Messages | `/user-messages` | Private admin chat + file sharing |
| Alerts | `/user-notifications` | In-app notification center |

### Admin portal

| Feature | URL | Description |
|---------|-----|-------------|
| Dashboard | `/admin-dashboard` | Admin home |
| Pending / All users | `/admin-pending-users`, `/admin-all-users` | User management |
| Messages | `/admin-messages` | User support inbox |
| Appointments | `/admin-appointments` | Confirm / reschedule bookings |
| Predictions | `/admin-prediction-history` | All users’ predict logs |
| Dataset | `/upload-dataset`, `/view-dataset` | CSV dataset management |
| Algorithms | `/algorithm-analysis`, etc. | Model training and comparison |

### Messaging and files

| Item | Detail |
|------|--------|
| Isolation | Each user has a separate conversation thread |
| Text | Optional caption with any message |
| Images | JPG, PNG, GIF, WEBP — shown as thumbnails |
| Documents | PDF, DOC, DOCX — download links |
| Max size | 10 MB per file |
| Storage | `media/support_messages/{user_id}/` |

### Notifications

| Trigger | User sees |
|---------|-----------|
| Admin replies in chat | Alert + Messages badge |
| Predict form submitted | Alert with result summary |
| Appointment updated | Alert with new status / slot |

---

## 10. URL map

### Public

| Path | Description |
|------|-------------|
| `/` | Home |
| `/about` | About |
| `/contact` | Contact |
| `/register` | User registration |
| `/userlogin` | User login |
| `/adminlogin` | Admin login |

### User (login required)

| Path | Description |
|------|-------------|
| `/user-dashboard` | Dashboard |
| `/user-profile` | Profile |
| `/user-predict` | Prediction form |
| `/user-prediction-history` | Prediction history list |
| `/user-prediction-history/<id>` | Single prediction detail |
| `/user-appointments` | Book / view appointments |
| `/user-chat` | Pregnancy assistant |
| `/user-messages` | Admin support chat |
| `/user-notifications` | Alerts |

### Admin (admin login required)

| Path | Description |
|------|-------------|
| `/admin-dashboard` | Dashboard |
| `/admin-pending-users` | Pending registrations |
| `/admin-all-users` | All users |
| `/admin-messages` | Message inbox |
| `/admin-messages/<user_sno>` | Chat with one user |
| `/admin-appointments` | Appointment management |
| `/admin-prediction-history` | All prediction runs |
| `/view-dataset` | View dataset |
| `/upload-dataset` | Upload dataset |
| `/algorithm-analysis` | Algorithm comparison |

---

## 11. Database tables

Django migrations manage these tables. Key ones:

| Table | App | Purpose |
|-------|-----|---------|
| `User Details` | mainapp | Registered users (legacy table name) |
| `user_predictions` | userapp | Latest predict result per user (one row each) |
| `prediction_history` | userapp | Every predict run (append-only log) |
| `appointments` | userapp | Consultation booking requests |
| `user_notifications` | userapp | In-app alerts for users |
| `chat_messages` | chatapp | Pregnancy assistant conversation history |
| `support_messages` | chatapp | User–admin private messages (+ file paths) |

---

## 12. Project structure

```
Maternity_assistance/
├── childbirth_proj/          # settings.py, urls.py, wsgi.py
├── mainapp/                  # home, register, admin login
├── userapp/                  # dashboard, predict, appointments, notifications
│   ├── models.py             # UserPrediction, PredictionHistory, Appointment, …
│   ├── prediction_store.py   # Save latest + history on predict
│   ├── context_processors.py # Unread badges for templates
│   └── management/commands/
│       ├── check_ml_pickles.py
│       └── seed_demo_user.py   # Fake data for college demos
├── adminapp/                 # admin dashboard, users, algorithms, appointments
├── chatapp/                  # pregnancy assistant + user–admin messaging
│   ├── data/pregnancy_tips.json
│   ├── services.py           # Gemini, tips, emergency checks
│   └── views.py              # user_chat, user_support, admin inbox
├── assets/
│   ├── templates/            # HTML (userapp, chatapp, adminapp, …)
│   │   └── userapp/includes/ # Shared user header + navbar
│   └── static/               # CSS, JS, images
├── media/                    # Uploads (user photos, support attachments)
├── childbirth.sql            # MySQL dump (schema + sample users)
├── encoder_newf.pkl          # Feature encoder
├── y_encoder.pkl             # Label encoder
├── XGB.pkl                   # Trained XGBoost model
├── ml_compat.py              # sklearn 1.2.x pickle compatibility
├── manage.py
├── requirements.txt
├── .env.example
└── .venv/                    # Local virtualenv (gitignored)
```

Prediction reads `encoder_newf.pkl`, `y_encoder.pkl`, and `XGB.pkl` from the **project root** when the user submits the predict form.

---

## 13. Configuration

### Environment variables (`.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `MYSQL_PASSWORD` | Yes | MySQL `root` password |
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `GEMINI_API_KEY` | No | Enables Gemini in pregnancy assistant |
| `GEMINI_MODEL` | No | Default: `gemini-2.5-flash` |

### Database (`childbirth_proj/settings.py`)

| Setting | Value |
|---------|--------|
| Database | `childbirth` |
| User | `root` |
| Password | from `.env` |
| Host | `localhost` |
| Port | `3306` |

### Pregnancy assistant notes

- API key belongs in `.env` only — never commit it.
- Without Gemini, quick topics and rule-based tips still work.
- Assistant is informational only, not medical advice. Severe symptoms trigger urgent-care messaging.
- If quota errors occur, try `GEMINI_MODEL=gemini-2.0-flash-lite` in `.env`.

---

## 14. Troubleshooting

### Server / Python

| Problem | Fix |
|---------|-----|
| `No module named 'pandas'` | Activate `.venv` and install dependencies (see [Step 1](#step-1--clone-and-create-a-virtual-environment)) |
| `NoReverseMatch` for a URL name | Restart `runserver`; confirm route exists in `childbirth_proj/urls.py` |
| Page 404 after git pull | Run `python manage.py migrate` and restart server |

Quick URL check:

```powershell
python manage.py shell -c "from django.urls import reverse; print(reverse('user_support'))"
```

Expected: `/user-messages`

### MySQL

| Problem | Fix |
|---------|-----|
| `net start MySQL80` — Access denied | Run PowerShell as **Administrator** |
| `ERROR 2003` — Can't connect | Start MySQL: `net start MySQL80` |
| `ERROR 1045` — Access denied for root | Fix `MYSQL_PASSWORD` in `.env` |
| `django.db.utils.OperationalError` | Confirm MySQL is running, database `childbirth` exists, re-import `childbirth.sql` if needed |

MySQL data-folder permission fix (if service stops immediately):

```powershell
icacls "C:\ProgramData\MySQL\MySQL Server 8.0\Data" /grant "NT AUTHORITY\NETWORK SERVICE:(OI)(CI)F" /T
net start MySQL80
```

### Migrations

```powershell
python manage.py migrate
python manage.py migrate chatapp
python manage.py migrate userapp
```

### ML prediction errors

**`'OrdinalEncoder' object has no attribute '_infrequent_enabled'`**

Pickles were saved with sklearn 1.2.x; newer Python may install sklearn 1.8+. The app patches encoders in `ml_compat.py`. Restart server after pulling fixes.

```powershell
python manage.py check_ml_pickles
```

Long-term: re-export `.pkl` files with the same sklearn/xgboost versions used in production.

### Template / static errors

| Problem | Fix |
|---------|-----|
| `Invalid block tag: 'static'` | Included templates need their own `{% load static %}` |
| Header looks different on some pages | All user pages use `userapp/includes/user-header.html` — pull latest templates |

### pip / requirements

If `pip install -r requirements.txt` fails on Python 3.13 (e.g. `PyYAML==6.0`), use the minimal install in [Step 1](#step-1--clone-and-create-a-virtual-environment).

---

## 15. Security (development only)

- `DEBUG = True` and default `SECRET_KEY` are for **local use only**.
- Do not deploy with sample passwords (`admin`/`admin`) or committed API keys.
- Store all secrets in `.env` (gitignored).
- Rotate `GEMINI_API_KEY` if it was ever committed or shared.

---

## 16. GitHub collaboration

### Clone and run (teammate quick start)

```powershell
git clone https://github.com/Bhupesh-zode/Maternity_assistance.git
cd Maternity_assistance

copy .env.example .env
notepad .env

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install Django==4.1.7 pandas scikit-learn xgboost Pillow mysqlclient google-generativeai

# Import childbirth.sql, set .env, then:
python manage.py migrate
python manage.py check_ml_pickles
python manage.py runserver

# Optional — before a college demo:
python manage.py seed_demo_user --email bhupeshzode9@gmail.com
```

### Branch workflow

```powershell
git pull
git checkout -b feature/short-description
git add .
git commit -m "Describe what you changed"
git push -u origin feature/short-description
```

Open a Pull Request on GitHub → review → merge → `git pull` on `main`.

### What Git tracks

| Committed | Ignored (`.gitignore`) |
|-----------|-------------------------|
| Source, templates, static assets | `.venv/`, old `childenv*` folders |
| `childbirth.sql`, `*.pkl` models | `.env` (passwords, API keys) |
| `requirements.txt`, `README.md`, `.env.example` | `media/` (uploads) |

---

## License / credits

Academic / project use. Dataset and model files are part of the original childbirth prediction project.
