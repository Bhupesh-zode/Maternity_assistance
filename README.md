# Maternity Assistance — Childbirth Prediction (Django)

Web application that predicts the recommended mode of childbirth (e.g. vaginal vs cesarean) using an XGBoost model. Includes a public site, user portal (predict, profile, **pregnancy assistant**), and admin portal (users, dataset, algorithm metrics).

**Repository:** [github.com/Bhupesh-zode/Maternity_assistance](https://github.com/Bhupesh-zode/Maternity_assistance)

**Stack:** Django 4.1.7 · MySQL 8 · scikit-learn · XGBoost · pandas · Google Gemini (`google-generativeai`)

---

## Features

| Area | What it does |
|------|----------------|
| **Public** | Home, about, contact, user registration |
| **User** | Login, dashboard, profile, ML prediction form |
| **Assistant** | Logged-in pregnancy chat at `/user-chat` — emergency keyword checks, curated tips (`chatapp/data/pregnancy_tips.json`), optional Gemini AI |
| **Admin** | Approve users, dataset upload/view, algorithm comparison (SVM, decision tree, KNN, random forest, AdaBoost, XGBoost, logistic regression) |

---

## Prerequisites

- **Python 3.10+** (developed with 3.13)
- **MySQL Server 8.0** (Windows service name: `MySQL80`)
- **Windows:** Visual C++ build tools may be required if `mysqlclient` fails to install (pre-built wheels usually work on 3.13)
- **Optional:** [Google AI Studio](https://aistudio.google.com/apikey) API key for the pregnancy assistant

---

## First-time setup

### 1. Clone and virtual environment

```powershell
git clone https://github.com/Bhupesh-zode/Maternity_assistance.git
cd Maternity_assistance

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
```

> Ignore old folders `childenv3.11.1` and `env_testing3` if present — they were copied from another machine. Use **`.venv`** only.

Minimal install (core packages only):

```powershell
pip install Django==4.1.7 pandas scikit-learn xgboost Pillow mysqlclient google-generativeai
```

### 2. Start MySQL

Open **PowerShell as Administrator**:

```powershell
net start MySQL80
```

If the service fails to start, see [Troubleshooting](#troubleshooting).

### 3. Import the database

Adjust the path to your clone location:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pYOUR_PASSWORD -e "source C:/path/to/Maternity_assistance/childbirth.sql"
```

Verify:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pYOUR_PASSWORD -e "USE childbirth; SHOW TABLES;"
```

### 4. Local secrets (`.env`)

```powershell
copy .env.example .env
notepad .env
```

Example `.env` (do **not** commit this file):

```env
MYSQL_PASSWORD=your_mysql_root_password
DJANGO_SECRET_KEY=change-me-to-a-random-secret-key

# Pregnancy assistant (https://aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

| Variable | Purpose |
|----------|---------|
| `MYSQL_PASSWORD` | MySQL `root` password (loaded into `settings.py`) |
| `DJANGO_SECRET_KEY` | Django secret key |
| `GEMINI_API_KEY` | Optional — enables Gemini replies in the assistant |
| `GEMINI_MODEL` | Optional — default `gemini-2.5-flash` |

Database connection (`childbirth_proj/settings.py`):

| Setting | Value |
|---------|--------|
| Database | `childbirth` |
| User | `root` |
| Password | from `.env` → `MYSQL_PASSWORD` |
| Host | `localhost` |
| Port | `3306` |

### 5. Django migrations

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py check
```

This creates Django tables including **`chat_messages`** for the pregnancy assistant (`chatapp`).

### 6. Run the server

```powershell
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

After pulling new code or changing `urls.py` / `settings.py`, **restart** `runserver` if pages fail with URL or settings errors.

---

## Daily use

```powershell
cd path\to\Maternity_assistance
.\.venv\Scripts\Activate.ps1

# Ensure MySQL is running (Admin PowerShell if stopped):
# net start MySQL80

python manage.py runserver
```

---

## Logins

### Admin portal

| Field | Value |
|-------|--------|
| URL | http://127.0.0.1:8000/adminlogin |
| Email | `admin` |
| Password | `admin` |

Hardcoded in `mainapp/views.py` (not stored in MySQL). Change before any public deployment.

### User portal (sample accounts from `childbirth.sql`)

| URL | Email | Password | Status |
|-----|-------|----------|--------|
| http://127.0.0.1:8000/userlogin | `deepika@gmail.com` | `Dee258369` | accepted |
| http://127.0.0.1:8000/userlogin | `admin@gmail.com` | `1234` | accepted |
| http://127.0.0.1:8000/userlogin | `marnus@gmail.com` | `Ma12346` | restricted |

New users register at `/register` with status **pending** until an admin approves them.

### Pregnancy assistant

| URL | http://127.0.0.1:8000/user-chat |
|-----|----------------------------------|
| Access | User login required (session `sno`) |
| Gemini | Optional — set `GEMINI_API_KEY` in `.env` |
| Without API key | Quick topics and rule-based / curated tips still work |

From the user dashboard, use **Assistant** in the navbar or the **Open assistant** card.

---

## Main URLs

| Path | Description |
|------|-------------|
| `/` | Home |
| `/register` | User registration |
| `/userlogin` | User login |
| `/user-dashboard` | User dashboard |
| `/user-predict` | Childbirth prediction form |
| `/user-profile` | User profile |
| `/user-chat` | Pregnancy assistant |
| `/adminlogin` | Admin login |
| `/admin-dashboard` | Admin dashboard |
| `/admin-all-users` | Manage users |
| `/admin-pending-users` | Approve pending users |
| `/view-dataset` | View dataset |
| `/algorithm-analysis` | Algorithm comparison |

---

## Pregnancy assistant (`chatapp`)

- **View:** `chatapp/views.py` → `user_chat`
- **Logic:** `chatapp/services.py` — emergency phrases, JSON tips, Gemini with model fallbacks
- **Data:** `chatapp/data/pregnancy_tips.json`
- **History:** `ChatMessage` model → MySQL table `chat_messages`
- **Auth:** Custom session check (`chatapp/utils.py` — `session["sno"]`)

**Safety:** The assistant is informational only, not medical advice. Severe symptoms trigger urgent-care messaging.

**Gemini notes:**

- Put your API key only in **`.env`**, never in `.env.example` or Git.
- Default model: `gemini-2.5-flash`. If you hit quota errors, try `gemini-2.0-flash-lite` in `.env`.
- Rotate your key if it was ever committed or shared.

---

## Project layout

```
Maternity_assistance/
├── childbirth_proj/       # settings.py, urls.py, wsgi.py
├── mainapp/               # home, register, admin login
├── userapp/               # user dashboard, predict (ML)
├── adminapp/              # admin dashboard, algorithms
├── chatapp/               # pregnancy assistant (Gemini + tips)
│   ├── data/pregnancy_tips.json
│   ├── services.py
│   ├── views.py
│   └── migrations/
├── assets/
│   ├── templates/         # HTML (userapp, chatapp, adminapp, …)
│   └── static/            # CSS, JS, images
├── media/                 # uploaded user images (gitignored)
├── childbirth.sql         # MySQL dump (schema + sample data)
├── encoder_newf.pkl       # feature encoder (prediction)
├── y_encoder.pkl          # label encoder
├── XGB.pkl                # trained XGBoost model
├── manage.py
├── ml_compat.py           # sklearn 1.2.x pickle loader (user + admin predict)
├── requirements.txt
├── .env.example           # template — copy to .env
└── .venv/                 # local virtual environment (gitignored)
```

Prediction reads `encoder_newf.pkl`, `y_encoder.pkl`, and `XGB.pkl` from the **project root** when the user submits the predict form.

---

## Troubleshooting

### `NoReverseMatch: 'user_chat' not found`

The template references `{% url 'user_chat' %}`, but the running server does not have that URL registered. Usually means:

1. You are on a branch **without** the `chatapp` changes — use `main` after merge, or branch `Feature-Chatbot-integration-for-safe-Pregnancy-Planning`.
2. **`chatapp`** is missing from `INSTALLED_APPS` in `childbirth_proj/settings.py`.
3. **`user-chat`** route is missing from `childbirth_proj/urls.py`.
4. The dev server is **stale** — stop it (Ctrl+C) and run `python manage.py runserver` again.

Quick check:

```powershell
python manage.py shell -c "from django.urls import reverse; print(reverse('user_chat'))"
```

Expected output: `/user-chat`

### `net start MySQL80` — Access is denied

Run PowerShell **as Administrator**.

### MySQL stops immediately — `Permission denied` on `BHUSHAN-bin.index`

Grant the service account access to the data folder (Admin PowerShell):

```powershell
icacls "C:\ProgramData\MySQL\MySQL Server 8.0\Data" /grant "NT AUTHORITY\NETWORK SERVICE:(OI)(CI)F" /T
net start MySQL80
```

Optional: comment out `log-bin="BHUSHAN-bin"` in `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini` if binary logging is not needed.

### `ERROR 1045` — Access denied for `root`

Test with your password:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pYOUR_PASSWORD -e "SELECT VERSION();"
```

Update `MYSQL_PASSWORD` in **`.env`**, not in Git.

### `ERROR 2003` — Can't connect (10061)

MySQL is not running. Start it: `net start MySQL80` (Administrator).

### Remove one-time password reset from `my.ini`

If you used `init_file=C:/mysql-pw-reset.txt` for setup, **remove that line** from `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`, then:

```powershell
net stop MySQL80
net start MySQL80
```

### Django `django.db.utils.OperationalError`

1. Confirm MySQL is running.
2. Confirm database exists: `SHOW DATABASES LIKE 'childbirth';`
3. Re-import `childbirth.sql` if the database is missing.
4. Check `MYSQL_PASSWORD` in `.env`.

### Assistant / `chat_messages` errors

```powershell
python manage.py migrate chatapp
```

Ensure `GEMINI_API_KEY` is set in `.env` for AI replies. Check the terminal for Gemini quota or API errors.

### Prediction errors after form submit

**`'OrdinalEncoder' object has no attribute '_infrequent_enabled'`**

The `.pkl` files were saved with **scikit-learn 1.2.1**, but Python 3.13 often installs a newer sklearn (e.g. 1.8). The app patches encoders on load in `ml_compat.py`. Restart `runserver` after pulling this fix, then submit the predict form again.

If you still see errors, check versions:

```powershell
python -c "import sklearn, xgboost; print(sklearn.__version__, xgboost.__version__)"
```

Long-term fix: re-export `encoder_newf.pkl`, `y_encoder.pkl`, and `XGB.pkl` with the same sklearn/xgboost versions you use in production.

**Smoke test** (loads all pickles + one sample prediction):

```powershell
python manage.py check_ml_pickles
```

Shared loader: `ml_compat.py` (used by `userapp` and `adminapp`).

**Note:** Admin “Gradient Boost” (`GradientBoostingClassifier.pkl`) may not load on sklearn 1.8+; XGBoost and logistic regression admin runs use the same compat loader for encoders.

---

## Security notes (development only)

- `DEBUG = True` and a dev-only default `SECRET_KEY` fallback are for local use only.
- Do not deploy with sample MySQL passwords, admin credentials, or committed API keys.
- Store secrets in **`.env`** only (listed in `.gitignore`).
- Rotate `GEMINI_API_KEY` if it was ever pasted into `.env.example` or pushed to GitHub.

---

## GitHub collaboration

### Install Git

Download [Git for Windows](https://git-scm.com/download/win). After install, restart PowerShell.

### Clone and run (teammate)

```powershell
git clone https://github.com/Bhupesh-zode/Maternity_assistance.git
cd Maternity_assistance

copy .env.example .env
notepad .env

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Import childbirth.sql, then:
python manage.py migrate
python manage.py runserver
```

### Branch workflow

```powershell
git pull
git checkout -b feature/short-description
# ... edit code ...
git add .
git commit -m "Describe what you changed"
git push -u origin feature/short-description
```

Open a **Pull Request** on GitHub to merge into `main`. Review, merge, then `git pull` on `main`.

**Chatbot feature branch (example):** `Feature-Chatbot-integration-for-safe-Pregnancy-Planning`

### What is tracked in Git

| Committed | Ignored (`.gitignore`) |
|-----------|-------------------------|
| Source code, templates, static assets | `.venv/`, old `childenv*` folders |
| `childbirth.sql`, `*.pkl` models | `.env` (passwords, API keys) |
| `requirements.txt`, `README.md`, `.env.example` | `media/` (uploads), `db.sqlite3` |
| `chatapp/` (assistant code + tips JSON) | Screen recordings (`*.mkv`, etc.) |

---

## License / credits

Academic / project use. Dataset and model files are part of the original childbirth prediction project.
