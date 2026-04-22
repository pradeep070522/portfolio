# 🚀 Django Portfolio

A modern, fully-dynamic personal portfolio website built with Django. All content — profile, skills, projects, and contact messages — is managed through the Django Admin panel. Zero hardcoded data.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2+-green?logo=django)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

---

## ✨ Features

### Portfolio Sections
| Section | Details |
|---|---|
| **Hero** | Profile photo with rotating gradient ring, name, tagline, stats, social links, floating tech chips |
| **About** | Bio, contact details, downloadable CV |
| **Skills** | Glassmorphism cards with animated progress bars, grouped by category |
| **Projects** | Cards with hover overlay, GitHub/Live links, tech tag pills, status badge |
| **Contact** | Email, WhatsApp, LinkedIn, GitHub links + AJAX contact form |

### Design
- **Dark glassmorphism** aesthetic with animated gradient orbs
- **Syne + Instrument Sans** font pairing
- CSS-only scroll reveal & skill bar animations
- Loading spinner with triple-ring animation
- Fully responsive — mobile-first
- SEO meta tags + Open Graph

### Backend
- Django models: `Profile`, `Skill`, `SkillCategory`, `Project`, `Message`
- Rich Django Admin with proficiency bars, image previews, inline editing
- Media upload support (profile photo, project images, resume PDF)
- AJAX contact form with JSON responses

---

## ⚠️ Python & Django Version Requirements

| Python | Django | Status |
|---|---|---|
| 3.12, 3.13, 3.14 | **5.1 / 5.2** ✅ | Fully supported |
| 3.10, 3.11 | 5.1 / 5.2 ✅ | Supported |
| 3.12+ | 4.2 ❌ | **Breaks admin** (`super` AttributeError) |

> **If you see `'super' object has no attribute 'dicts'` in admin — you have Django 4.x with Python 3.12+.**
> Fix: `pip install "django>=5.1,<6"` — this project's `requirements.txt` already specifies this.

## 🛠 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourname/portfolio.git
cd portfolio

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
# requirements.txt pins Django>=5.1 which supports Python 3.10–3.14
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum
```

### 3. Database

```bash
python manage.py migrate

# Load demo data (optional — recommended for first run)
python manage.py seed_data
```

### 4. Admin user

```bash
python manage.py createsuperuser
```

### 5. Run

```bash
python manage.py runserver
```

- **Portfolio:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

---

## 📂 Project Structure

```
portfolio_site/
├── manage.py
├── requirements.txt
├── .env.example
│
├── portfolio_project/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── portfolio/                  # Main app
│   ├── models.py               # Profile, Skill, Project, Message
│   ├── views.py                # Index + AJAX contact handler
│   ├── forms.py                # ContactForm
│   ├── admin.py                # Rich admin configuration
│   ├── urls.py                 # App URL patterns
│   ├── templates/
│   │   └── portfolio/
│   │       └── index.html      # Single-page portfolio template
│   └── management/
│       └── commands/
│           └── seed_data.py    # Demo data seeder
│
├── static/
│   ├── css/style.css           # Full glassmorphism stylesheet
│   └── js/main.js              # Loader, reveal, skills, AJAX form
│
└── media/                      # Uploaded images (gitignored)
    └── uploads/
```

---

## ⚙️ Admin Panel Guide

Visit `/admin/` and log in with your superuser credentials.

| Model | What you can do |
|---|---|
| **Profile** | Update name, bio, tagline, photo, contact details, social links, resume PDF, stats |
| **Skill Categories** | Group skills (Frontend, Backend, DevOps…) with drag-and-drop ordering |
| **Skills** | Add/edit skills with icon, proficiency slider, category, visibility toggle |
| **Projects** | Add projects with image, description, tech stack, GitHub/Live URLs, status |
| **Messages** | Read contact form submissions, mark as read |

> **Tip:** Only one Profile record is allowed. The admin will hide the "Add" button once it exists.

---

## 🌐 Deployment (Production)

### Environment changes

In `.env`:
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=a-long-random-secret-key
```

### Collect static files

```bash
python manage.py collectstatic
```

### Run with Gunicorn + Nginx (recommended)

```bash
gunicorn portfolio_project.wsgi:application --bind 0.0.0.0:8000
```

Point Nginx to `localhost:8000` and serve `/static/` and `/media/` directories directly.

### Platforms

Works out of the box on **Railway**, **Render**, **Heroku**, **DigitalOcean App Platform**, and **VPS (Ubuntu/Nginx)**.

---

## 📝 Customisation Tips

- **Change colours:** Edit CSS variables at the top of `static/css/style.css`
- **Add a new section:** Add the HTML block to `index.html`, a model in `models.py`, pass data in `views.py`
- **Enable email notifications:** Set `EMAIL_*` variables in `.env` and call `send_mail()` inside `views.send_message`

---

## 📄 License

MIT — free to use, modify, and distribute.
