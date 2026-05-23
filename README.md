# Childbirth Prediction (Django)

Web application that predicts the recommended mode of childbirth (e.g. vaginal vs cesarean) using an XGBoost model. Includes a public site, user portal (predict, profile), and admin portal (users, dataset, algorithm metrics).

**Stack:** Django 4.1.7 · MySQL 8 · scikit-learn · XGBoost · pandas

---

## Prerequisites

- **Python 3.10+** (developed with 3.13)
- **MySQL Server 8.0** (Windows service name: `MySQL80`)
- **Windows:** Visual C++ build tools may be required if `mysqlclient` fails to install (pre-built wheels usually work on 3.13)

---

## First-time setup

### 1. Virtual environment and dependencies

From the project folder:

```powershell
cd "C:\Users\bhush\Desktop\Childbirth  project\Chidbirth_final"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install Django==4.1.7 pandas scikit-learn xgboost Pillow mysqlclient
```

Or install everything from the lockfile (may take longer):

```powershell
pip install -r requirements.txt
```

> Ignore old folders `childenv3.11.1` and `env_testing3` — they were copied from another machine. Use **`.venv`** only.

### 2. Start MySQL

Open **PowerShell as Administrator**:

```powershell
net start MySQL80
```

If the service fails to start, see [Troubleshooting](#troubleshooting) below.

### 3. Import the database

In a normal PowerShell window (project folder not required):

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pchildbirth123 -e "source C:/Users/bhush/Desktop/Childbirth  project/Chidbirth_final/childbirth.sql"
```

Verify:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pchildbirth123 -e "USE childbirth; SHOW TABLES;"
```

### 4. Local secrets (`.env`)

Copy the example file and set your MySQL root password:

```powershell
copy .env.example .env
notepad .env
```

Example `.env`:

```env
MYSQL_PASSWORD=childbirth123
DJANGO_SECRET_KEY=your-random-secret-key
```

Database connection in `childbirth_proj/settings.py`:

| Setting  | Value        |
|----------|--------------|
| Database | `childbirth` |
| User     | `root`       |
| Password | from `.env` → `MYSQL_PASSWORD` |
| Host     | `localhost`  |
| Port     | `3306`       |

`.env` is **not** committed to Git (see [GitHub collaboration](#github-collaboration)).

### 5. Django migrations

```powershell
cd "C:\Users\bhush\Desktop\Childbirth  project\Chidbirth_final"
.\.venv\Scripts\Activate.ps1

python manage.py migrate
python manage.py check
```

### 6. Run the server

```powershell
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

---

## Daily use

```powershell
cd "C:\Users\bhush\Desktop\Childbirth  project\Chidbirth_final"
.\.venv\Scripts\Activate.ps1

# Ensure MySQL is running (Admin PowerShell if stopped):
# net start MySQL80

python manage.py runserver
```

---

## Logins

### Admin portal

| Field    | Value    |
|----------|----------|
| URL      | http://127.0.0.1:8000/adminlogin |
| Email    | `admin`  |
| Password | `admin`  |

Hardcoded in `mainapp/views.py` (not stored in MySQL).

### User portal (from `childbirth.sql`)

| URL | Email | Password | Status |
|-----|-------|----------|--------|
| http://127.0.0.1:8000/userlogin | `deepika@gmail.com` | `Dee258369` | accepted |
| http://127.0.0.1:8000/userlogin | `admin@gmail.com` | `1234` | accepted |
| http://127.0.0.1:8000/userlogin | `marnus@gmail.com` | `Ma12346` | restricted |

New users register at `/register` with status **pending** until an admin approves them.

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
| `/adminlogin` | Admin login |
| `/admin-dashboard` | Admin dashboard |
| `/admin-all-users` | Manage users |
| `/admin-pending-users` | Approve pending users |
| `/view-dataset` | View dataset |
| `/algorithm-analysis` | Algorithm comparison |

---

## Project layout

```
Chidbirth_final/
├── childbirth_proj/     # settings.py, urls.py, wsgi.py
├── mainapp/             # home, register, admin login
├── userapp/             # user dashboard, predict (ML)
├── adminapp/            # admin dashboard, algorithms
├── assets/
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
├── media/               # uploaded user images
├── childbirth.sql       # MySQL dump (schema + sample data)
├── encoder_newf.pkl     # feature encoder (prediction)
├── y_encoder.pkl        # label encoder
├── XGB.pkl              # trained XGBoost model
├── manage.py
├── requirements.txt
└── .venv/               # local virtual environment
```

Prediction reads `encoder_newf.pkl`, `y_encoder.pkl`, and `XGB.pkl` from the **project root** when the user submits the predict form.

---

## Troubleshooting

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

Root has a password. Test with:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pchildbirth123 -e "SELECT VERSION();"
```

Update `PASSWORD` in `childbirth_proj/settings.py` to match your MySQL root password.

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
4. Check `MYSQL_PASSWORD` in your `.env` file.

### Prediction errors after form submit

Often caused by scikit-learn / XGBoost version mismatch with the `.pkl` files. Use the versions in `requirements.txt`, or retrain/export models with your installed library versions.

---

## Security notes (development only)

- `DEBUG = True` and a default `SECRET_KEY` are set for local development only.
- Do not deploy with the sample MySQL password or admin credentials without changing them.
- Prefer environment variables or a `.env` file (not committed) for production secrets.

---

## GitHub collaboration

### One-time: install Git

Download [Git for Windows](https://git-scm.com/download/win). After install, restart PowerShell. If `git` is not found, use the full path: `"C:\Program Files\Git\bin\git.exe"`.

### Repository owner (first push)

1. Create an empty repo on GitHub (e.g. `childbirth-prediction`). **Private** is recommended. Do not add a README if this project already has one.

2. In the project folder:

```powershell
cd "C:\Users\bhush\Desktop\Childbirth  project\Chidbirth_final"

git init
git add .
git status
git commit -m "Initial commit: Django childbirth prediction app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Review `git status` before committing: `.venv`, `.env`, and `media/` must **not** appear.

3. Invite your teammate: GitHub repo → **Settings** → **Collaborators** → **Add people**.

### Teammate (clone and run)

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

copy .env.example .env
notepad .env

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Import childbirth.sql, then:
python manage.py migrate
python manage.py runserver
```

### Daily workflow

```powershell
git pull
git checkout -b feature/short-description
# ... edit code ...
git add .
git commit -m "Describe what you changed"
git push -u origin feature/short-description
```

Open a **Pull Request** on GitHub to merge into `main`. The other person reviews and merges, then runs `git pull` on `main`.

### What is tracked in Git

| Committed | Ignored (`.gitignore`) |
|-----------|-------------------------|
| Source code, templates, static assets | `.venv/`, old `childenv*` folders |
| `childbirth.sql`, `*.pkl` models | `.env` (passwords) |
| `requirements.txt`, `README.md` | `media/` (uploads), `db.sqlite3` |

---

## License / credits

Academic / project use. Dataset and model files are part of the original childbirth prediction project.
